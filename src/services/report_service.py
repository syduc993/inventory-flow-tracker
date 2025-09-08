# src/services/report_service.py

from datetime import datetime, timedelta
from collections import defaultdict
from src.utils.larkbase import larkbase_get_all
import logging
import json


logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self, app_token, table_id):
        self.app_token = app_token
        self.table_id = table_id





    def get_daily_report(self, user_id=None, start_date_str=None, end_date_str=None, employee_filter=None, from_depot_filter=None, to_depot_filter=None, transport_provider_filter=None):
        """Lấy báo cáo hàng ngày - có thể lọc theo nhiều tiêu chí và nhóm theo ngày"""
        logger.info(f"🔍 Starting daily report generation with filters: employee={employee_filter}, from_depot={from_depot_filter}, to_depot={to_depot_filter}, transport={transport_provider_filter}")
        
        try:
            # Tính toán timestamp range
            if start_date_str and end_date_str:
                start_report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_report_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                start_timestamp = int(start_report_date.timestamp() * 1000)
                end_timestamp = int((end_report_date + timedelta(days=1)).timestamp() * 1000)
                logger.info(f"📅 Date range filter: {start_date_str} to {end_date_str} (timestamps: {start_timestamp} - {end_timestamp})")
            elif start_date_str:
                report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                start_timestamp = int(report_date.timestamp() * 1000)
                end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
                logger.info(f"📅 Single date filter: {start_date_str} (timestamps: {start_timestamp} - {end_timestamp})")
            else:
                start_timestamp = 0
                end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
                logger.info(f"📅 No date filter - using full range (timestamps: {start_timestamp} - {end_timestamp})")
            
            logger.info(f"📊 Getting all records from data source...")
            all_records = larkbase_get_all(self.app_token, self.table_id)
            logger.info(f"📈 Retrieved {len(all_records)} total records from database")
            
            filtered_records = []
            date_filtered_count = 0
            employee_filtered_count = 0
            from_depot_filtered_count = 0
            to_depot_filtered_count = 0
            transport_filtered_count = 0
            
            for record in all_records:
                fields = record.get('fields', {})
                
                # Lọc theo khoảng ngày
                if start_date_str or end_date_str:
                    handover_date = fields.get('Ngày bàn giao')
                    if handover_date:
                        try:
                            handover_timestamp = int(handover_date)
                            if not (start_timestamp <= handover_timestamp < end_timestamp):
                                date_filtered_count += 1
                                continue
                        except (ValueError, TypeError):
                            date_filtered_count += 1
                            continue
                
                # Các filter khác
                if employee_filter and employee_filter.strip() and fields.get('ID người bàn giao', '') != employee_filter:
                    employee_filtered_count += 1
                    continue
                if from_depot_filter and from_depot_filter.strip() and fields.get('ID kho đi', '') != from_depot_filter:
                    from_depot_filtered_count += 1
                    continue
                if to_depot_filter and to_depot_filter.strip() and fields.get('ID kho đến', '') != to_depot_filter:
                    to_depot_filtered_count += 1
                    continue
                
                # Filter theo đơn vị vận chuyển
                if transport_provider_filter and transport_provider_filter.strip():
                    transport_provider_record = (fields.get('Đơn vị vận chuyển') or '').strip()
                    if transport_provider_record != transport_provider_filter:
                        transport_filtered_count += 1
                        continue
                
                filtered_records.append(fields)
            
            # Log thống kê filter
            logger.info(f"🎯 Filter statistics:")
            logger.info(f"   - Date filtered out: {date_filtered_count} records")
            logger.info(f"   - Employee filtered out: {employee_filtered_count} records")
            logger.info(f"   - From depot filtered out: {from_depot_filtered_count} records")
            logger.info(f"   - To depot filtered out: {to_depot_filtered_count} records")
            logger.info(f"   - Transport provider filtered out: {transport_filtered_count} records")
            logger.info(f"✅ Final result: {len(filtered_records)} records match all filters")
            
            if len(filtered_records) == 0:
                logger.warning("⚠️ No records found matching the specified filters")
            
            logger.info(f"🔢 Processing filtered records for daily statistics calculation...")
            result = self._calculate_daily_statistics_grouped_by_date(filtered_records)
            logger.info(f"✅ Daily report generation completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting daily report: {e}")
            logger.error(f"   - Parameters: start_date={start_date_str}, end_date={end_date_str}")
            logger.error(f"   - Filters: employee={employee_filter}, from_depot={from_depot_filter}, to_depot={to_depot_filter}, transport={transport_provider_filter}")
            return self._empty_report_data()



    # def get_daily_report(self, user_id=None, start_date_str=None, end_date_str=None, employee_filter=None, from_depot_filter=None, to_depot_filter=None, transport_provider_filter=None):  # ✅ THÊM transport_provider_filter
    #     """Lấy báo cáo hàng ngày - có thể lọc theo nhiều tiêu chí và nhóm theo ngày"""
    #     try:
    #         if start_date_str and end_date_str:
    #             start_report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             end_report_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    #             start_timestamp = int(start_report_date.timestamp() * 1000)
    #             end_timestamp = int((end_report_date + timedelta(days=1)).timestamp() * 1000)
    #         elif start_date_str:
    #             report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             start_timestamp = int(report_date.timestamp() * 1000)
    #             end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
    #         else:
    #             start_timestamp = 0
    #             end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
    #         all_records = larkbase_get_all(self.app_token, self.table_id)
            
    #         filtered_records = []
    #         for record in all_records:
    #             fields = record.get('fields', {})
                
    #             # Lọc theo khoảng ngày
    #             if start_date_str or end_date_str:
    #                 handover_date = fields.get('Ngày bàn giao')
    #                 if handover_date:
    #                     try:
    #                         handover_timestamp = int(handover_date)
    #                         if not (start_timestamp <= handover_timestamp < end_timestamp):
    #                             continue
    #                     except (ValueError, TypeError):
    #                         continue
                
    #             # Các filter khác
    #             if employee_filter and employee_filter.strip() and fields.get('ID người bàn giao', '') != employee_filter:
    #                 continue
    #             if from_depot_filter and from_depot_filter.strip() and fields.get('ID kho đi', '') != from_depot_filter:
    #                 continue
    #             if to_depot_filter and to_depot_filter.strip() and fields.get('ID kho đến', '') != to_depot_filter:
    #                 continue
                
    #             # ✅ THÊM: Filter theo đơn vị vận chuyển
    #             if transport_provider_filter and transport_provider_filter.strip():
    #                 transport_provider_record = fields.get('Đơn vị vận chuyển', '').strip()
    #                 if transport_provider_record != transport_provider_filter:
    #                     continue
                
    #             filtered_records.append(fields)
            
    #         logger.info(f"Found {len(filtered_records)} records after filtering")
            
    #         return self._calculate_daily_statistics_grouped_by_date(filtered_records)
            
    #     except Exception as e:
    #         logger.error(f"Error getting daily report: {e}")
    #         return self._empty_report_data()


    def get_all_transport_providers(self):
        """Lấy danh sách tất cả đơn vị vận chuyển từ records"""
        try:
            all_records = larkbase_get_all(self.app_token, self.table_id)
            providers = {}
            for record in all_records:
                fields = record.get('fields', {})
                provider_name = fields.get('Đơn vị vận chuyển')
                if provider_name and provider_name.strip() and provider_name not in providers:
                    providers[provider_name] = provider_name
            return [{'id': provider, 'name': provider} for provider in sorted(providers.keys())]
        except Exception as e:
            logger.error(f"Error getting transport providers: {e}")
            return []


    # def get_daily_report(self, user_id=None, start_date_str=None, end_date_str=None, employee_filter=None, from_depot_filter=None, to_depot_filter=None):
    #     """Lấy báo cáo hàng ngày - có thể lọc theo nhiều tiêu chí và nhóm theo ngày"""
    #     try:
    #         if start_date_str and end_date_str:
    #             start_report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             end_report_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    #             start_timestamp = int(start_report_date.timestamp() * 1000)
    #             end_timestamp = int((end_report_date + timedelta(days=1)).timestamp() * 1000)
    #         elif start_date_str:
    #             report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             start_timestamp = int(report_date.timestamp() * 1000)
    #             end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
    #         else:
    #             start_timestamp = 0
    #             end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
    #         all_records = larkbase_get_all(self.app_token, self.table_id)
            
    #         filtered_records = []
    #         for record in all_records:
    #             fields = record.get('fields', {})
                
    #             # Lọc theo khoảng ngày
    #             if start_date_str or end_date_str:
    #                 handover_date = fields.get('Ngày bàn giao')
    #                 if handover_date:
    #                     try:
    #                         handover_timestamp = int(handover_date)
    #                         if not (start_timestamp <= handover_timestamp < end_timestamp):
    #                             continue
    #                     except (ValueError, TypeError):
    #                         continue
                
    #             # Các filter khác (employee, depot) giữ nguyên như cũ
    #             if employee_filter and employee_filter.strip() and fields.get('ID người bàn giao', '') != employee_filter:
    #                 continue
    #             if from_depot_filter and from_depot_filter.strip() and fields.get('ID kho đi', '') != from_depot_filter:
    #                 continue
    #             if to_depot_filter and to_depot_filter.strip() and fields.get('ID kho đến', '') != to_depot_filter:
    #                 continue
                
    #             filtered_records.append(fields)
            
    #         logger.info(f"Found {len(filtered_records)} records after filtering")
            
    #         # ✅ SỬA: Gọi hàm mới để tính toán nhóm theo ngày
    #         return self._calculate_daily_statistics_grouped_by_date(filtered_records)
            
    #     except Exception as e:
    #         logger.error(f"Error getting daily report: {e}")
    #         return self._empty_report_data()

    def _calculate_daily_statistics_grouped_by_date(self, records):
        """Tính toán thống kê từ danh sách records với nhóm theo ngày bàn giao"""
        if not records:
            return self._empty_report_data()
        
        # ✅ THÊM: Nhóm records theo ngày bàn giao
        daily_groups = defaultdict(list)
        
        for fields in records:
            # Chuyển đổi timestamp thành ngày (YYYY-MM-DD)
            handover_date = fields.get('Ngày bàn giao')
            date_str = 'Unknown'
            
            if handover_date:
                try:
                    # Chuyển từ mili giây sang giây, sau đó tạo datetime object
                    timestamp_sec = int(handover_date) / 1000
                    dt_obj = datetime.fromtimestamp(timestamp_sec)
                    # Chuyển về múi giờ GMT+7 (như trong record_routes.py)
                    #dt_obj_gmt7 = dt_obj + timedelta(hours=7)
                    dt_obj_gmt7 = dt_obj # Nguyên nhân là do dưới larkbase đã lưu Ngày bàn giao theo GMT + 7
                    date_str = dt_obj_gmt7.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    date_str = 'Unknown'
            
            daily_groups[date_str].append(fields)
        
        # ✅ THÊM: Tính toán thống kê cho từng ngày
        daily_statistics = {}
        route_summary_by_date = defaultdict(list)
        transport_summary_by_date = defaultdict(list)
        
        for date_str, date_records in daily_groups.items():
            # Sử dụng logic cũ để tính toán cho từng ngày
            grouped_records = self._group_records_by_group_id(date_records)
            
            route_transport_stats = defaultdict(lambda: {'count': 0, 'bags': 0, 'loads': 0})
            total_loads = 0
            
            for group_key, group_records in grouped_records.items():
                if group_key.startswith('group_'):
                    loads_added = self._process_grouped_records(group_records, route_transport_stats, total_loads)
                    total_loads += loads_added
                else:
                    for fields in group_records:
                        loads_added = self._process_single_record(fields, route_transport_stats)
                        total_loads += loads_added
            
            # Tạo route summary cho ngày này
            daily_route_summary = []
            for route_transport_key, stats in route_transport_stats.items():
                route_part, transport_part = route_transport_key.split('|', 1)
                daily_route_summary.append({
                    'date': date_str,  # ✅ THÊM: Cột ngày
                    'route': route_part,
                    'transport_provider': transport_part,
                    'count': stats['count'],
                    'bags': stats['bags'],
                    'loads': stats['loads']
                })
            
            daily_route_summary.sort(key=lambda x: x['loads'], reverse=True)
            route_summary_by_date[date_str] = daily_route_summary
            
            # Tính toán transport summary cho ngày này
            transport_stats = defaultdict(lambda: {'count': 0, 'bags': 0, 'loads': 0, 'routes': set()})
            
            for item in daily_route_summary:
                provider = item['transport_provider']
                stats = transport_stats[provider]
                
                stats['count'] += item['count']
                stats['bags'] += item['bags']
                stats['loads'] += item['loads']
                stats['routes'].add(item['route'])
            
            daily_transport_summary = []
            for provider, stats in transport_stats.items():
                daily_transport_summary.append({
                    'date': date_str,  # ✅ THÊM: Cột ngày
                    'transport_provider': provider,
                    'count': stats['count'],
                    'bags': stats['bags'],
                    'loads': stats['loads'],
                    'route_count': len(stats['routes'])
                })
                
            daily_transport_summary.sort(key=lambda x: x['loads'], reverse=True)
            transport_summary_by_date[date_str] = daily_transport_summary
            
            # Lưu thống kê tổng cho ngày
            daily_statistics[date_str] = {
                'total_records': len(date_records),
                'total_quantity': total_loads,
                'route_summary': daily_route_summary,
                'transport_summary': daily_transport_summary
            }
        
        # ✅ THÊM: Tạo tổng hợp toàn bộ các ngày để hiển thị
        all_route_summary = []
        all_transport_summary = []
        
        for date_str in sorted(daily_statistics.keys()):
            all_route_summary.extend(route_summary_by_date[date_str])
            all_transport_summary.extend(transport_summary_by_date[date_str])
        
        # Tính tổng toàn bộ
        total_records = sum(stats['total_records'] for stats in daily_statistics.values())
        total_quantity = sum(stats['total_quantity'] for stats in daily_statistics.values())
        
        return {
            'total_records': total_records,
            'total_quantity': total_quantity,
            'route_summary': all_route_summary,  # ✅ SỬA: Có cột date
            'transport_summary': all_transport_summary,  # ✅ SỬA: Có cột date
            'daily_statistics': daily_statistics,  # ✅ THÊM: Thống kê theo từng ngày
            'date_list': sorted([d for d in daily_statistics.keys() if d != 'Unknown'])  # ✅ THÊM: Danh sách ngày
        }











    # def get_daily_report(self, user_id=None, start_date_str=None, end_date_str=None, employee_filter=None, from_depot_filter=None, to_depot_filter=None):
    #     """Lấy báo cáo hàng ngày - có thể lọc theo nhiều tiêu chí"""
    #     try:
    #         if start_date_str and end_date_str:
    #             # Tính toán với khoảng thời gian từ start_date đến end_date
    #             start_report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             end_report_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                
    #             # Timestamp bắt đầu từ 00:00:00 của ngày bắt đầu
    #             start_timestamp = int(start_report_date.timestamp() * 1000)
    #             # Timestamp kết thúc đến 00:00:00 của ngày tiếp theo sau end_date
    #             end_timestamp = int((end_report_date + timedelta(days=1)).timestamp() * 1000)
    #         elif start_date_str:
    #             # Nếu chỉ có start_date, dùng như ngày đơn lẻ
    #             report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             start_timestamp = int(report_date.timestamp() * 1000)
    #             end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
    #         else:
    #             # Không có filter ngày - lấy tất cả
    #             start_timestamp = 0
    #             end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
    #         all_records = larkbase_get_all(self.app_token, self.table_id)
            
    #         filtered_records = []
    #         for record in all_records:
    #             fields = record.get('fields', {})
                
    #             # Lọc theo khoảng ngày nếu có start_date_str hoặc end_date_str
    #             if start_date_str or end_date_str:
    #                 handover_date = fields.get('Ngày bàn giao')
    #                 if handover_date:
    #                     try:
    #                         handover_timestamp = int(handover_date)
    #                         if not (start_timestamp <= handover_timestamp < end_timestamp):
    #                             continue
    #                     except (ValueError, TypeError):
    #                         continue
                
    #             # Lọc theo nhân viên bàn giao
    #             if employee_filter and employee_filter.strip() and fields.get('ID người bàn giao', '') != employee_filter:
    #                 continue

    #             # Lọc theo kho đi
    #             if from_depot_filter and from_depot_filter.strip() and fields.get('ID kho đi', '') != from_depot_filter:
    #                 continue

    #             # Lọc theo kho đến
    #             if to_depot_filter and to_depot_filter.strip() and fields.get('ID kho đến', '') != to_depot_filter:
    #                 continue
                
    #             # Record đã pass tất cả filters, thêm vào kết quả
    #             filtered_records.append(fields)
            
    #         logger.info(f"Found {len(filtered_records)} records after filtering")
            
    #         return self._calculate_daily_statistics(filtered_records)
            
    #     except Exception as e:
    #         logger.error(f"Error getting daily report: {e}")
    #         return self._empty_report_data()




    def get_all_employees(self):
        """Lấy danh sách tất cả nhân viên từ records"""
        try:
            all_records = larkbase_get_all(self.app_token, self.table_id)
            employees = {}
            for record in all_records:
                fields = record.get('fields', {})
                emp_id = fields.get('ID người bàn giao')
                emp_name = fields.get('Người bàn giao')
                if emp_id and emp_name and emp_id not in employees:
                    employees[emp_id] = emp_name
            return [{'id': emp_id, 'name': emp_name} for emp_id, emp_name in employees.items()]
        except Exception as e:
            logger.error(f"Error getting employees: {e}")
            return []


    def get_all_depots(self):
        """Lấy danh sách tất cả depots từ records"""
        try:
            all_records = larkbase_get_all(self.app_token, self.table_id)
            depots = {}
            for record in all_records:
                fields = record.get('fields', {})
                from_id = fields.get('ID kho đi')
                from_name = fields.get('Kho đi')
                if from_id and from_name and from_id not in depots:
                    depots[from_id] = from_name
                to_id = fields.get('ID kho đến')
                to_name = fields.get('Kho đến')
                if to_id and to_name and to_id not in depots:
                    depots[to_id] = to_name
            return [{'id': depot_id, 'name': depot_name} for depot_id, depot_name in depots.items()]
        except Exception as e:
            logger.error(f"Error getting depots: {e}")
            return []

    def _empty_report_data(self):
        """Trả về dữ liệu rỗng cho báo cáo"""
        return {
            'total_records': 0,
            'total_quantity': 0,
            'transport_providers': {},
            'routes': {},
            'transport_summary': [],
            'route_summary': []
        }

    def _calculate_daily_statistics(self, records):
        """Tính toán thống kê từ danh sách records với logic nhóm theo Group ID"""
        if not records:
            return self._empty_report_data()
        
        # === BƯỚC 1: NHÓM RECORDS THEO GROUP ID ===
        grouped_records = self._group_records_by_group_id(records)
        
        route_transport_stats = defaultdict(lambda: {'count': 0, 'bags': 0, 'loads': 0})
        total_loads = 0
        
        # === BƯỚC 2: XỬ LÝ TỪNG NHÓM RECORDS ===
        for group_key, group_records in grouped_records.items():
            if group_key.startswith('group_'):
                # Records có Group ID - chỉ tính "Số lượng bao" 1 lần cho cả nhóm
                self._process_grouped_records(group_records, route_transport_stats, total_loads)
            else:
                # Records không có Group ID - tính bình thường từng record
                for fields in group_records:
                    loads_added = self._process_single_record(fields, route_transport_stats)
                    total_loads += loads_added
        
        # === BƯỚC 3: TẠO SUMMARY CHO BẢNG TUYẾN ĐƯỜNG ===
        route_summary = []
        for route_transport_key, stats in route_transport_stats.items():
            route_part, transport_part = route_transport_key.split('|', 1)
            route_summary.append({
                'route': route_part,
                'transport_provider': transport_part,
                'count': stats['count'],
                'bags': stats['bags'],
                'loads': stats['loads']
            })
        
        route_summary.sort(key=lambda x: x['loads'], reverse=True)
        
        # === BƯỚC 4: TÍNH TOÁN CHO BẢNG ĐƠN VỊ VẬN CHUYỂN ===
        transport_stats = defaultdict(lambda: {'count': 0, 'bags': 0, 'loads': 0, 'routes': set()})
        
        for item in route_summary:
            provider = item['transport_provider']
            stats = transport_stats[provider]
            
            stats['count'] += item['count']
            stats['bags'] += item['bags']
            stats['loads'] += item['loads']
            stats['routes'].add(item['route'])

        transport_summary = []
        for provider, stats in transport_stats.items():
            transport_summary.append({
                'transport_provider': provider,
                'count': stats['count'],
                'bags': stats['bags'],
                'loads': stats['loads'],
                'route_count': len(stats['routes']) # Đếm số tuyến đường duy nhất
            })
            
        transport_summary.sort(key=lambda x: x['loads'], reverse=True)
        
        return {
            'total_records': len(records),
            'total_quantity': total_loads,
            'routes': dict(route_transport_stats),
            'route_summary': route_summary,
            'transport_providers': dict(transport_stats),
            'transport_summary': transport_summary
        }

    def _group_records_by_group_id(self, records):
        """Nhóm records theo Group ID"""
        grouped = {}
        single_counter = 0
        
        for fields in records:
            group_id = fields.get('Group ID')
            
            if group_id:
                # Records có Group ID giống nhau sẽ được nhóm lại
                group_key = f"group_{group_id}"
                if group_key not in grouped:
                    grouped[group_key] = []
                grouped[group_key].append(fields)
            else:
                # Records không có Group ID tạo key riêng
                single_counter += 1
                single_key = f"single_{single_counter}"
                grouped[single_key] = [fields]
        
        return grouped


    def _process_grouped_records(self, group_records, route_transport_stats, total_loads):
        """Xử lý nhóm records có cùng Group ID - chỉ tính 'Số lượng bao' 1 lần"""
        if not group_records:
            return 0
        
        # Lấy thông tin chung từ record đầu tiên
        first_record = group_records[0]
        
        # ✅ SỬA: Khởi tạo biến bags trước vòng lặp
        total_bags = 0
        
        # Tính tổng bags từ tất cả records trong nhóm
        for fields in group_records:
            try:
                bags_field = fields.get('Số lượng túi', 0)
                if isinstance(bags_field, str):
                    bags = int(bags_field) if bags_field.isdigit() else 0
                elif isinstance(bags_field, (int, float)):
                    bags = int(bags_field)
                else:
                    bags = 0  # ✅ THÊM: Default value nếu không phải str/int/float
                total_bags += bags
            except (ValueError, TypeError):
                # ✅ THÊM: Nếu có lỗi, tiếp tục với giá trị 0
                continue
        
        # Chỉ lấy "Số lượng bao" từ record đầu tiên (đại diện cho cả nhóm)
        loads = 0
        try:
            loads_field = first_record.get('Số lượng bao', first_record.get('Số lượng tải', first_record.get('Số lượng bao/tải giao', 0)))
            if isinstance(loads_field, str):
                loads = int(loads_field) if loads_field.isdigit() else 0
            elif isinstance(loads_field, (int, float)):
                loads = int(loads_field)
            else:
                loads = 0  # ✅ THÊM: Default value
        except (ValueError, TypeError):
            loads = 0  # ✅ THÊM: Default value nếu có lỗi
        
        # Tạo route key từ record đầu tiên
        transport_provider = (first_record.get('Đơn vị vận chuyển') or 'Không rõ').strip()
        from_depot = (first_record.get('Kho đi') or 'Không rõ').strip()
        to_depot = (first_record.get('Kho đến') or 'Không rõ').strip()
        route_key = f"{from_depot} → {to_depot}"
        route_transport_key = f"{route_key}|{transport_provider}"
        
        # Cập nhật thống kê
        stats = route_transport_stats[route_transport_key]
        stats['count'] += len(group_records)  # Đếm tất cả records trong nhóm
        stats['bags'] += total_bags          # Tổng bags của cả nhóm
        stats['loads'] += loads              # Chỉ tính loads 1 lần
        
        return loads





    # def _process_grouped_records(self, group_records, route_transport_stats, total_loads):
    #     """Xử lý nhóm records có cùng Group ID - chỉ tính 'Số lượng bao' 1 lần"""
    #     if not group_records:
    #         return 0
        
    #     # Lấy thông tin chung từ record đầu tiên
    #     first_record = group_records[0]
        
    #     # Tính tổng bags từ tất cả records trong nhóm
    #     total_bags = 0
    #     for fields in group_records:
    #         try:
    #             bags_field = fields.get('Số lượng túi', 0)
    #             if isinstance(bags_field, str):
    #                 bags = int(bags_field) if bags_field.isdigit() else 0
    #             elif isinstance(bags_field, (int, float)):
    #                 bags = int(bags_field)
    #             total_bags += bags
    #         except (ValueError, TypeError):
    #             pass
        
    #     # Chỉ lấy "Số lượng bao" từ record đầu tiên (đại diện cho cả nhóm)
    #     loads = 0
    #     try:
    #         loads_field = first_record.get('Số lượng bao', first_record.get('Số lượng tải', first_record.get('Số lượng bao/tải giao', 0)))
    #         if isinstance(loads_field, str):
    #             loads = int(loads_field) if loads_field.isdigit() else 0
    #         elif isinstance(loads_field, (int, float)):
    #             loads = int(loads_field)
    #     except (ValueError, TypeError):
    #         pass
        
    #     # Tạo route key từ record đầu tiên
    #     transport_provider = (first_record.get('Đơn vị vận chuyển') or 'Không rõ').strip()
    #     from_depot = (first_record.get('Kho đi') or 'Không rõ').strip()
    #     to_depot = (first_record.get('Kho đến') or 'Không rõ').strip()
    #     route_key = f"{from_depot} → {to_depot}"
    #     route_transport_key = f"{route_key}|{transport_provider}"
        
    #     # Cập nhật thống kê
    #     stats = route_transport_stats[route_transport_key]
    #     stats['count'] += len(group_records)  # Đếm tất cả records trong nhóm
    #     stats['bags'] += total_bags          # Tổng bags của cả nhóm
    #     stats['loads'] += loads              # Chỉ tính loads 1 lần
        
    #     return loads

    def _process_single_record(self, fields, route_transport_stats):
        """Xử lý record đơn lẻ không có Group ID"""
        bags = 0
        try:
            bags_field = fields.get('Số lượng túi', 0)
            if isinstance(bags_field, str):
                bags = int(bags_field) if bags_field.isdigit() else 0
            elif isinstance(bags_field, (int, float)):
                bags = int(bags_field)
        except (ValueError, TypeError):
            pass
            
        loads = 0
        try:
            loads_field = fields.get('Số lượng bao', fields.get('Số lượng tải', fields.get('Số lượng bao/tải giao', 0)))
            if isinstance(loads_field, str):
                loads = int(loads_field) if loads_field.isdigit() else 0
            elif isinstance(loads_field, (int, float)):
                loads = int(loads_field)
        except (ValueError, TypeError):
            pass
        
        transport_provider = (fields.get('Đơn vị vận chuyển') or 'Không rõ').strip()
        from_depot = (fields.get('Kho đi') or 'Không rõ').strip()
        to_depot = (fields.get('Kho đến') or 'Không rõ').strip()
        route_key = f"{from_depot} → {to_depot}"
        route_transport_key = f"{route_key}|{transport_provider}"
        
        stats = route_transport_stats[route_transport_key]
        stats['count'] += 1
        stats['bags'] += bags
        stats['loads'] += loads
        
        return loads



    # def _calculate_daily_statistics(self, records):
    #     """Tính toán thống kê từ danh sách records"""
    #     if not records:
    #         return self._empty_report_data()
        
    #     route_transport_stats = defaultdict(lambda: {'count': 0, 'bags': 0, 'loads': 0})
    #     total_loads = 0
        
    #     for fields in records:
    #         bags = 0
    #         try:
    #             # SỬA LỖI 1: Lấy đúng dữ liệu cho "SL túi" từ cột "Số lượng túi"
    #             bags_field = fields.get('Số lượng túi', 0)
    #             if isinstance(bags_field, str):
    #                 bags = int(bags_field) if bags_field.isdigit() else 0
    #             elif isinstance(bags_field, (int, float)):
    #                 bags = int(bags_field)
    #         except (ValueError, TypeError):
    #             pass
                
    #         loads = 0
    #         try:
    #             # SỬA LỖI 2: Lấy đúng dữ liệu cho "SL bao" từ cột "Số lượng bao"
    #             loads_field = fields.get('Số lượng bao', fields.get('Số lượng tải', fields.get('Số lượng bao/tải giao', 0)))
    #             if isinstance(loads_field, str):
    #                 loads = int(loads_field) if loads_field.isdigit() else 0
    #             elif isinstance(loads_field, (int, float)):
    #                 loads = int(loads_field)
    #             total_loads += loads
    #         except (ValueError, TypeError):
    #             pass
            
    #         transport_provider = (fields.get('Đơn vị vận chuyển') or 'Không rõ').strip()
    #         from_depot = (fields.get('Kho đi') or 'Không rõ').strip()
    #         to_depot = (fields.get('Kho đến') or 'Không rõ').strip()
    #         route_key = f"{from_depot} → {to_depot}"
    #         route_transport_key = f"{route_key}|{transport_provider}"
            
    #         stats = route_transport_stats[route_transport_key]
    #         stats['count'] += 1
    #         stats['bags'] += bags
    #         stats['loads'] += loads
        
    #     # --- Tính toán cho Bảng Tuyến đường ---
    #     route_summary = []
    #     for route_transport_key, stats in route_transport_stats.items():
    #         route_part, transport_part = route_transport_key.split('|', 1)
    #         route_summary.append({
    #             'route': route_part,
    #             'transport_provider': transport_part,
    #             'count': stats['count'],
    #             'bags': stats['bags'],
    #             'loads': stats['loads']
    #         })
        
    #     route_summary.sort(key=lambda x: x['loads'], reverse=True)
        
    #     # === BỔ SUNG: TÍNH TOÁN CHO BẢNG ĐƠN VỊ VẬN CHUYỂN ===
    #     transport_stats = defaultdict(lambda: {'count': 0, 'bags': 0, 'loads': 0, 'routes': set()})
        
    #     for item in route_summary:
    #         provider = item['transport_provider']
    #         stats = transport_stats[provider]
            
    #         stats['count'] += item['count']
    #         stats['bags'] += item['bags']
    #         stats['loads'] += item['loads']
    #         stats['routes'].add(item['route'])

    #     transport_summary = []
    #     for provider, stats in transport_stats.items():
    #         transport_summary.append({
    #             'transport_provider': provider,
    #             'count': stats['count'],
    #             'bags': stats['bags'],
    #             'loads': stats['loads'],
    #             'route_count': len(stats['routes']) # Đếm số tuyến đường duy nhất
    #         })
            
    #     transport_summary.sort(key=lambda x: x['loads'], reverse=True)
    #     # === KẾT THÚC PHẦN BỔ SUNG ===
        
    #     return {
    #         'total_records': len(records),
    #         'total_quantity': total_loads,
    #         'routes': dict(route_transport_stats),
    #         'route_summary': route_summary,
    #         'transport_providers': dict(transport_stats),
    #         'transport_summary': transport_summary # Trả về dữ liệu đã được tính toán
    #     }


    def export_route_records_to_excel(self, from_depot, to_depot, start_date_str=None, end_date_str=None, employee_filter=None, transport_provider_filter=None):  # ✅ THÊM transport_provider_filter
        """Xuất records của một tuyến đường cụ thể ra Excel với hỗ trợ date range"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            import io
            
            # Xử lý date range logic (giữ nguyên như cũ)
            if start_date_str and end_date_str:
                start_report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_report_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                start_timestamp = int(start_report_date.timestamp() * 1000)
                end_timestamp = int((end_report_date + timedelta(days=1)).timestamp() * 1000)
            elif start_date_str:
                report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                start_timestamp = int(report_date.timestamp() * 1000)
                end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
            else:
                start_timestamp = 0
                end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
            all_records = larkbase_get_all(self.app_token, self.table_id)
            
            route_records = []
            for record in all_records:
                fields = record.get('fields', {})
                
                # Filter theo date range
                if start_date_str or end_date_str:
                    handover_date = fields.get('Ngày bàn giao')
                    if handover_date:
                        try:
                            handover_timestamp = int(handover_date)
                            if not (start_timestamp <= handover_timestamp < end_timestamp):
                                continue
                        except (ValueError, TypeError):
                            continue
                
                # Filter theo employee
                if employee_filter and fields.get('ID người bàn giao', '') != employee_filter:
                    continue
                
                # ✅ THÊM: Filter theo transport provider
                if transport_provider_filter and transport_provider_filter.strip():
                    transport_provider_record = fields.get('Đơn vị vận chuyển', '').strip()
                    if transport_provider_record != transport_provider_filter:
                        continue
                    
                # Filter theo route
                if fields.get('Kho đi', '').strip() == from_depot and fields.get('Kho đến', '').strip() == to_depot:
                    route_records.append(fields)
            
            # Logic tạo Excel file giữ nguyên như cũ...
            if not route_records:
                return None, 0
            
            grouped_records = self._group_records_for_export(route_records)
            
            wb = Workbook()
            ws = wb.active
            
            # Cập nhật title để reflect transport provider filter nếu có
            title_parts = [f"{from_depot} → {to_depot}"]
            if start_date_str and end_date_str and start_date_str != end_date_str:
                title_parts.append(f"({start_date_str} to {end_date_str})")
            elif start_date_str:
                title_parts.append(f"({start_date_str})")
            if transport_provider_filter:
                title_parts.append(f"[{transport_provider_filter}]")
                
            ws.title = " ".join(title_parts)[:31]  # Excel limit 31 chars
            
            # Phần tạo Excel table giữ nguyên như trong code cũ...
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            headers = ["ID", "Số lượng túi", "Số lượng bao", "Số lượng sản phẩm yêu cầu", "ID người bàn giao", "Người bàn giao"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font, cell.fill, cell.alignment = header_font, header_fill, header_alignment
            current_row = 2
            
            for group_key, group_records in grouped_records.items():
                if len(group_records) > 1:
                    # Nhóm có nhiều records - merge cột "Số lượng bao"
                    first_record = group_records[0]
                    
                    # Ghi row đầu tiên
                    ws.cell(row=current_row, column=1, value=first_record.get('ID', ''))
                    ws.cell(row=current_row, column=2, value=first_record.get('Số lượng túi', 0))
                    ws.cell(row=current_row, column=3, value=first_record.get('Số lượng bao', 0))
                    ws.cell(row=current_row, column=4, value=first_record.get('Số lượng sản phẩm yêu cầu', 0))
                    ws.cell(row=current_row, column=5, value=first_record.get('ID người bàn giao', ''))
                    ws.cell(row=current_row, column=6, value=first_record.get('Người bàn giao', ''))
                    
                    # Merge cột "Số lượng bao" vertically cho group
                    if len(group_records) > 1:
                        ws.merge_cells(
                            start_row=current_row, start_column=3,
                            end_row=current_row + len(group_records) - 1, end_column=3
                        )
                    
                    # Ghi các rows còn lại
                    for i, record in enumerate(group_records[1:], 1):
                        ws.cell(row=current_row + i, column=1, value=record.get('ID', ''))
                        ws.cell(row=current_row + i, column=2, value=record.get('Số lượng túi', 0))
                        # Column 3 đã merge, không ghi gì
                        ws.cell(row=current_row + i, column=4, value=record.get('Số lượng sản phẩm yêu cầu', 0))
                        ws.cell(row=current_row + i, column=5, value=record.get('ID người bàn giao', ''))
                        ws.cell(row=current_row + i, column=6, value=record.get('Người bàn giao', ''))
                    
                    current_row += len(group_records)
                else:
                    # Single record - không merge
                    record = group_records[0]
                    ws.cell(row=current_row, column=1, value=record.get('ID', ''))
                    ws.cell(row=current_row, column=2, value=record.get('Số lượng túi', 0))
                    ws.cell(row=current_row, column=3, value=record.get('Số lượng bao', 0))
                    ws.cell(row=current_row, column=4, value=record.get('Số lượng sản phẩm yêu cầu', 0))
                    ws.cell(row=current_row, column=5, value=record.get('ID người bàn giao', ''))
                    ws.cell(row=current_row, column=6, value=record.get('Người bàn giao', ''))
                    current_row += 1
            
            # Auto adjust columns
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except: 
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)
            return excel_buffer, len(route_records)
            
        except Exception as e:
            logger.error(f"Error creating route Excel export: {e}")
            return None, 0


    # def export_route_records_to_excel(self, from_depot, to_depot, start_date_str=None, end_date_str=None, employee_filter=None):
    #     """Xuất records của một tuyến đường cụ thể ra Excel với hỗ trợ date range"""
    #     try:
    #         from openpyxl import Workbook
    #         from openpyxl.styles import Font, PatternFill, Alignment
    #         import io
            
    #         # ✅ SỬA: Xử lý date range thay vì single date
    #         if start_date_str and end_date_str:
    #             # Tính toán với khoảng thời gian từ start_date đến end_date
    #             start_report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             end_report_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                
    #             # Timestamp bắt đầu từ 00:00:00 của ngày bắt đầu
    #             start_timestamp = int(start_report_date.timestamp() * 1000)
    #             # Timestamp kết thúc đến 00:00:00 của ngày tiếp theo sau end_date
    #             end_timestamp = int((end_report_date + timedelta(days=1)).timestamp() * 1000)
    #         elif start_date_str:
    #             # Nếu chỉ có start_date, dùng như ngày đơn lẻ
    #             report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             start_timestamp = int(report_date.timestamp() * 1000)
    #             end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
    #         else:
    #             # Không có filter ngày - lấy tất cả
    #             start_timestamp = 0
    #             end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
    #         all_records = larkbase_get_all(self.app_token, self.table_id)
            
    #         route_records = []
    #         for record in all_records:
    #             fields = record.get('fields', {})
                
    #             # ✅ SỬA: Filter theo date range nếu có start_date_str hoặc end_date_str
    #             if start_date_str or end_date_str:
    #                 handover_date = fields.get('Ngày bàn giao')
    #                 if handover_date:
    #                     try:
    #                         handover_timestamp = int(handover_date)
    #                         if not (start_timestamp <= handover_timestamp < end_timestamp):
    #                             continue
    #                     except (ValueError, TypeError):
    #                         continue
                
    #             # Filter theo employee
    #             if employee_filter and fields.get('ID người bàn giao', '') != employee_filter:
    #                 continue
                    
    #             # Filter theo route
    #             if fields.get('Kho đi', '').strip() == from_depot and fields.get('Kho đến', '').strip() == to_depot:
    #                 route_records.append(fields)
            
    #         if not route_records:
    #             return None, 0
            
    #         grouped_records = self._group_records_for_export(route_records)
            
    #         wb = Workbook()
    #         ws = wb.active
            
    #         # ✅ SỬA: Cập nhật title để reflect date range
    #         if start_date_str and end_date_str and start_date_str != end_date_str:
    #             ws.title = f"{from_depot} → {to_depot} ({start_date_str} to {end_date_str})"[:31]  # Excel limit 31 chars
    #         elif start_date_str:
    #             ws.title = f"{from_depot} → {to_depot} ({start_date_str})"[:31]
    #         else:
    #             ws.title = f"{from_depot} → {to_depot}"[:31]
            
    #         header_font = Font(bold=True, color="FFFFFF")
    #         header_fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
    #         header_alignment = Alignment(horizontal="center", vertical="center")
            
    #         # ✅ THÊM: Cột "Số lượng sản phẩm yêu cầu" vào headers
    #         headers = ["ID", "Số lượng túi", "Số lượng bao", "Số lượng sản phẩm yêu cầu", "ID người bàn giao", "Người bàn giao"]
    #         for col, header in enumerate(headers, 1):
    #             cell = ws.cell(row=1, column=col, value=header)
    #             cell.font, cell.fill, cell.alignment = header_font, header_fill, header_alignment
    #         current_row = 2
            
    #         for group_key, group_records in grouped_records.items():
    #             if len(group_records) > 1:
    #                 # ✅ MERGE: Nhóm có nhiều records - merge cột "Số lượng bao"
    #                 first_record = group_records[0]
                    
    #                 # Ghi row đầu tiên
    #                 ws.cell(row=current_row, column=1, value=first_record.get('ID', ''))
    #                 ws.cell(row=current_row, column=2, value=first_record.get('Số lượng túi', 0))
    #                 ws.cell(row=current_row, column=3, value=first_record.get('Số lượng bao', 0))
    #                 # ✅ THÊM: Cột "Số lượng sản phẩm yêu cầu"
    #                 ws.cell(row=current_row, column=4, value=first_record.get('Số lượng sản phẩm yêu cầu', 0))
    #                 ws.cell(row=current_row, column=5, value=first_record.get('ID người bàn giao', ''))
    #                 ws.cell(row=current_row, column=6, value=first_record.get('Người bàn giao', ''))
                    
    #                 # Merge cột "Số lượng bao" vertically cho group
    #                 if len(group_records) > 1:
    #                     ws.merge_cells(
    #                         start_row=current_row, start_column=3,
    #                         end_row=current_row + len(group_records) - 1, end_column=3
    #                     )
                    
    #                 # Ghi các rows còn lại
    #                 for i, record in enumerate(group_records[1:], 1):
    #                     ws.cell(row=current_row + i, column=1, value=record.get('ID', ''))
    #                     ws.cell(row=current_row + i, column=2, value=record.get('Số lượng túi', 0))
    #                     # Column 3 đã merge, không ghi gì
    #                     # ✅ THÊM: Cột "Số lượng sản phẩm yêu cầu" cho các rows còn lại
    #                     ws.cell(row=current_row + i, column=4, value=record.get('Số lượng sản phẩm yêu cầu', 0))
    #                     ws.cell(row=current_row + i, column=5, value=record.get('ID người bàn giao', ''))
    #                     ws.cell(row=current_row + i, column=6, value=record.get('Người bàn giao', ''))
                    
    #                 current_row += len(group_records)
    #             else:
    #                 # Single record - không merge
    #                 record = group_records[0]
    #                 ws.cell(row=current_row, column=1, value=record.get('ID', ''))
    #                 ws.cell(row=current_row, column=2, value=record.get('Số lượng túi', 0))
    #                 ws.cell(row=current_row, column=3, value=record.get('Số lượng bao', 0))
    #                 # ✅ THÊM: Cột "Số lượng sản phẩm yêu cầu" cho single record
    #                 ws.cell(row=current_row, column=4, value=record.get('Số lượng sản phẩm yêu cầu', 0))
    #                 ws.cell(row=current_row, column=5, value=record.get('ID người bàn giao', ''))
    #                 ws.cell(row=current_row, column=6, value=record.get('Người bàn giao', ''))
    #                 current_row += 1
            
    #         # Auto adjust columns
    #         for column in ws.columns:
    #             max_length = 0
    #             column_letter = column[0].column_letter
    #             for cell in column:
    #                 try:
    #                     if len(str(cell.value)) > max_length:
    #                         max_length = len(str(cell.value))
    #                 except: 
    #                     pass
    #             adjusted_width = min(max_length + 2, 50)
    #             ws.column_dimensions[column_letter].width = adjusted_width
            
    #         excel_buffer = io.BytesIO()
    #         wb.save(excel_buffer)
    #         excel_buffer.seek(0)
    #         return excel_buffer, len(route_records)
            
    #     except Exception as e:
    #         logger.error(f"Error creating route Excel export: {e}")
    #         return None, 0



    # def export_route_records_to_excel(self, from_depot, to_depot, start_date_str=None, end_date_str=None, employee_filter=None):
    #     """Xuất records của một tuyến đường cụ thể ra Excel với hỗ trợ date range"""
    #     try:
    #         from openpyxl import Workbook
    #         from openpyxl.styles import Font, PatternFill, Alignment
    #         import io
            
    #         # ✅ SỬA: Xử lý date range thay vì single date
    #         if start_date_str and end_date_str:
    #             # Tính toán với khoảng thời gian từ start_date đến end_date
    #             start_report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             end_report_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                
    #             # Timestamp bắt đầu từ 00:00:00 của ngày bắt đầu
    #             start_timestamp = int(start_report_date.timestamp() * 1000)
    #             # Timestamp kết thúc đến 00:00:00 của ngày tiếp theo sau end_date
    #             end_timestamp = int((end_report_date + timedelta(days=1)).timestamp() * 1000)
    #         elif start_date_str:
    #             # Nếu chỉ có start_date, dùng như ngày đơn lẻ
    #             report_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #             start_timestamp = int(report_date.timestamp() * 1000)
    #             end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
    #         else:
    #             # Không có filter ngày - lấy tất cả
    #             start_timestamp = 0
    #             end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
    #         all_records = larkbase_get_all(self.app_token, self.table_id)
            
    #         route_records = []
    #         for record in all_records:
    #             fields = record.get('fields', {})
                
    #             # ✅ SỬA: Filter theo date range nếu có start_date_str hoặc end_date_str
    #             if start_date_str or end_date_str:
    #                 handover_date = fields.get('Ngày bàn giao')
    #                 if handover_date:
    #                     try:
    #                         handover_timestamp = int(handover_date)
    #                         if not (start_timestamp <= handover_timestamp < end_timestamp):
    #                             continue
    #                     except (ValueError, TypeError):
    #                         continue
                
    #             # Filter theo employee
    #             if employee_filter and fields.get('ID người bàn giao', '') != employee_filter:
    #                 continue
                    
    #             # Filter theo route
    #             if fields.get('Kho đi', '').strip() == from_depot and fields.get('Kho đến', '').strip() == to_depot:
    #                 route_records.append(fields)
            
    #         if not route_records:
    #             return None, 0
            
    #         grouped_records = self._group_records_for_export(route_records)
            
    #         wb = Workbook()
    #         ws = wb.active
            
    #         # ✅ SỬA: Cập nhật title để reflect date range
    #         if start_date_str and end_date_str and start_date_str != end_date_str:
    #             ws.title = f"{from_depot} → {to_depot} ({start_date_str} to {end_date_str})"[:31]  # Excel limit 31 chars
    #         elif start_date_str:
    #             ws.title = f"{from_depot} → {to_depot} ({start_date_str})"[:31]
    #         else:
    #             ws.title = f"{from_depot} → {to_depot}"[:31]
            
    #         header_font = Font(bold=True, color="FFFFFF")
    #         header_fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
    #         header_alignment = Alignment(horizontal="center", vertical="center")
            
    #         headers = ["ID", "Số lượng túi", "Số lượng bao", "ID người bàn giao", "Người bàn giao"]
    #         for col, header in enumerate(headers, 1):
    #             cell = ws.cell(row=1, column=col, value=header)
    #             cell.font, cell.fill, cell.alignment = header_font, header_fill, header_alignment
    #         current_row = 2
            
    #         for group_key, group_records in grouped_records.items():
    #             if len(group_records) > 1:
    #                 # ✅ MERGE: Nhóm có nhiều records - merge cột "Số lượng bao"
    #                 first_record = group_records[0]
                    
    #                 # Ghi row đầu tiên
    #                 ws.cell(row=current_row, column=1, value=first_record.get('ID', ''))
    #                 ws.cell(row=current_row, column=2, value=first_record.get('Số lượng túi', 0))
    #                 ws.cell(row=current_row, column=3, value=first_record.get('Số lượng bao', 0))
    #                 ws.cell(row=current_row, column=4, value=first_record.get('ID người bàn giao', ''))
    #                 ws.cell(row=current_row, column=5, value=first_record.get('Người bàn giao', ''))
                    
    #                 # Merge cột "Số lượng bao" vertically cho group
    #                 if len(group_records) > 1:
    #                     ws.merge_cells(
    #                         start_row=current_row, start_column=3,
    #                         end_row=current_row + len(group_records) - 1, end_column=3
    #                     )
                    
    #                 # Ghi các rows còn lại
    #                 for i, record in enumerate(group_records[1:], 1):
    #                     ws.cell(row=current_row + i, column=1, value=record.get('ID', ''))
    #                     ws.cell(row=current_row + i, column=2, value=record.get('Số lượng túi', 0))
    #                     # Column 3 đã merge, không ghi gì
    #                     ws.cell(row=current_row + i, column=4, value=record.get('ID người bàn giao', ''))
    #                     ws.cell(row=current_row + i, column=5, value=record.get('Người bàn giao', ''))
                    
    #                 current_row += len(group_records)
    #             else:
    #                 # Single record - không merge
    #                 record = group_records[0]
    #                 ws.cell(row=current_row, column=1, value=record.get('ID', ''))
    #                 ws.cell(row=current_row, column=2, value=record.get('Số lượng túi', 0))
    #                 ws.cell(row=current_row, column=3, value=record.get('Số lượng bao', 0))
    #                 ws.cell(row=current_row, column=4, value=record.get('ID người bàn giao', ''))
    #                 ws.cell(row=current_row, column=5, value=record.get('Người bàn giao', ''))
    #                 current_row += 1
            
    #         # Auto adjust columns
    #         for column in ws.columns:
    #             max_length = 0
    #             column_letter = column[0].column_letter
    #             for cell in column:
    #                 try:
    #                     if len(str(cell.value)) > max_length:
    #                         max_length = len(str(cell.value))
    #                 except: 
    #                     pass
    #             adjusted_width = min(max_length + 2, 50)
    #             ws.column_dimensions[column_letter].width = adjusted_width
            
    #         excel_buffer = io.BytesIO()
    #         wb.save(excel_buffer)
    #         excel_buffer.seek(0)
    #         return excel_buffer, len(route_records)
            
    #     except Exception as e:
    #         logger.error(f"Error creating route Excel export: {e}")
    #         return None, 0





    def _group_records_for_export(self, records):
        """
        Nhóm các records theo Group ID để merge cells trong Excel
        
        Args:
            records (list): Danh sách các field records
            
        Returns:
            dict: {group_key: [list_of_records], ...}
        """
        grouped = {}
        single_counter = 0
        
        for record in records:
            group_id = record.get('Group ID')
            
            if group_id:
                # Records có Group ID giống nhau sẽ được group lại
                if group_id not in grouped:
                    grouped[group_id] = []
                grouped[group_id].append(record)
            else:
                # Records không có Group ID sẽ tạo key riêng
                single_counter += 1
                single_key = f"single_{single_counter}"
                grouped[single_key] = [record]
        
        return grouped
