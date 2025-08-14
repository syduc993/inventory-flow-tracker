# # src/services/report_service.py
# from datetime import datetime, timedelta
# from collections import defaultdict
# from src.utils.larkbase import larkbase_get_all
# import logging
# import json

# logger = logging.getLogger(__name__)

# class ReportService:
#     def __init__(self, app_token, table_id):
#         self.app_token = app_token
#         self.table_id = table_id

#     def get_daily_report(self, user_id, date_str):
#         """Lấy báo cáo hàng ngày cho user"""
#         try:
#             # Parse date
#             report_date = datetime.strptime(date_str, '%Y-%m-%d')
#             start_timestamp = int(report_date.timestamp() * 1000)
#             end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
            
#             # ✅ THÊM: Lấy employee ID tương ứng với Lark user ID
#             employee_id = self._get_employee_id_from_user_id(user_id)
#             if not employee_id:
#                 logger.warning(f"Không tìm thấy employee ID cho user {user_id}")
#                 return self._empty_report_data()
            
#             logger.info(f"Mapping: Lark user {user_id} -> Employee ID {employee_id}")
            
#             # Lấy tất cả records
#             all_records = larkbase_get_all(self.app_token, self.table_id)
            
#             # Filter records của employee trong ngày
#             user_records = []
#             for record in all_records:
#                 fields = record.get('fields', {})
                
#                 # ✅ SỬA: Check employee ID thay vì user ID
#                 record_user_id = fields.get('ID người bàn giao', '')
#                 if record_user_id != employee_id:
#                     continue
                
#                 # Check date
#                 handover_date = fields.get('Ngày bàn giao')
#                 if not handover_date:
#                     continue
                    
#                 try:
#                     handover_timestamp = int(handover_date)
#                     if start_timestamp <= handover_timestamp < end_timestamp:
#                         user_records.append(fields)
#                 except (ValueError, TypeError):
#                     continue
            
#             logger.info(f"Found {len(user_records)} records for employee {employee_id} on {date_str}")
            
#             # Tính toán thống kê
#             return self._calculate_daily_statistics(user_records)
            
#         except Exception as e:
#             logger.error(f"Error getting daily report: {e}")
#             return self._empty_report_data()

#     def _get_employee_id_from_user_id(self, lark_user_id):
#         """Mapping tạm thời để test"""
#         # ✅ TEST: Hardcode mapping cho user hiện tại
#         user_mapping = {
#             'ou_04bf3b2ad306e6bb53f5fe06ad8e492c': 'AM.0051'  # DA. Lê Sỹ Đức -> AM.0051
#         }
#         return user_mapping.get(lark_user_id)

#     def _empty_report_data(self):
#         """Trả về dữ liệu rỗng cho báo cáo"""
#         return {
#             'total_records': 0,
#             'total_quantity': 0,
#             'transport_providers': {},
#             'routes': {},
#             'transport_summary': [],
#             'route_summary': []
#         }


#     def _calculate_daily_statistics(self, records):
#         """Tính toán thống kê từ danh sách records"""
#         if not records:
#             return {
#                 'total_records': 0,
#                 'total_quantity': 0,
#                 'transport_providers': {},
#                 'routes': {},
#                 'transport_summary': [],
#                 'route_summary': []
#             }
        
#         transport_stats = defaultdict(lambda: {'count': 0, 'quantity': 0})
#         route_stats = defaultdict(lambda: {'count': 0, 'quantity': 0, 'transport_providers': set()})
        
#         total_quantity = 0
        
#         for fields in records:
#             # Số lượng bao/tải - thử nhiều tên field
#             quantity = 0
#             quantity_field = (fields.get('Số lượng bao/tải giao') or 
#                              fields.get('SoLuongBaoTaiGiao') or 
#                              fields.get('HandoverQuantity') or 
#                              fields.get('Quantity', 0))
            
#             try:
#                 if isinstance(quantity_field, str):
#                     quantity = int(quantity_field) if quantity_field.isdigit() else 0
#                 elif isinstance(quantity_field, (int, float)):
#                     quantity = int(quantity_field)
#                 total_quantity += quantity
#             except (ValueError, TypeError):
#                 logger.warning(f"Error parsing quantity: {quantity_field}")
#                 pass
            
#             # Đơn vị vận chuyển - thử nhiều tên field
#             transport_provider = (fields.get('Đơn vị vận chuyển') or 
#                                  fields.get('DonViVanChuyen') or 
#                                  fields.get('TransportProvider') or 
#                                  'Không rõ').strip()
            
#             if transport_provider:
#                 transport_stats[transport_provider]['count'] += 1
#                 transport_stats[transport_provider]['quantity'] += quantity
            
#             # Route (kho đi -> kho đến) - thử nhiều tên field
#             from_depot = (fields.get('Kho đi') or 
#                          fields.get('KhoDi') or 
#                          fields.get('FromDepot') or 
#                          'Không rõ').strip()
            
#             to_depot = (fields.get('Kho đến') or 
#                        fields.get('KhoDen') or 
#                        fields.get('ToDepot') or 
#                        'Không rõ').strip()
            
#             route_key = f"{from_depot} → {to_depot}"
            
#             route_stats[route_key]['count'] += 1
#             route_stats[route_key]['quantity'] += quantity
#             if transport_provider:
#                 route_stats[route_key]['transport_providers'].add(transport_provider)
        
#         # Chuyển đổi sang format cho template
#         transport_summary = []
#         for provider, stats in transport_stats.items():
#             transport_summary.append({
#                 'name': provider,
#                 'count': stats['count'],
#                 'quantity': stats['quantity']
#             })
        
#         route_summary = []
#         for route, stats in route_stats.items():
#             route_summary.append({
#                 'route': route,
#                 'count': stats['count'],
#                 'quantity': stats['quantity'],
#                 'transport_providers': list(stats['transport_providers'])
#             })
        
#         # Sắp xếp theo số lượng giảm dần
#         transport_summary.sort(key=lambda x: x['quantity'], reverse=True)
#         route_summary.sort(key=lambda x: x['quantity'], reverse=True)
        
#         return {
#             'total_records': len(records),
#             'total_quantity': total_quantity,
#             'transport_providers': dict(transport_stats),
#             'routes': dict(route_stats),
#             'transport_summary': transport_summary,
#             'route_summary': route_summary
#         }

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

    def get_daily_report(self, user_id=None, date_str=None, employee_filter=None, from_depot_filter=None, to_depot_filter=None):
        """Lấy báo cáo hàng ngày - có thể lọc theo nhiều tiêu chí"""
        try:
            # Parse date
            if date_str:
                report_date = datetime.strptime(date_str, '%Y-%m-%d')
                start_timestamp = int(report_date.timestamp() * 1000)
                end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
            else:
                # Lấy tất cả nếu không có date
                start_timestamp = 0
                end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
            # Lấy tất cả records
            all_records = larkbase_get_all(self.app_token, self.table_id)
            
            # Filter records
            filtered_records = []
            for record in all_records:
                fields = record.get('fields', {})
                
                # Filter by date nếu có
                if date_str:
                    handover_date = fields.get('Ngày bàn giao')
                    if handover_date:
                        try:
                            handover_timestamp = int(handover_date)
                            if not (start_timestamp <= handover_timestamp < end_timestamp):
                                continue
                        except (ValueError, TypeError):
                            continue
                
                # Filter by employee nếu có
                if employee_filter:
                    record_employee_id = fields.get('ID người bàn giao', '')
                    if record_employee_id != employee_filter:
                        continue
                
                # Filter by from depot nếu có
                if from_depot_filter:
                    from_depot_id = fields.get('ID kho đi', '')
                    if from_depot_id != from_depot_filter:
                        continue
                
                # Filter by to depot nếu có
                if to_depot_filter:
                    to_depot_id = fields.get('ID kho đến', '')
                    if to_depot_id != to_depot_filter:
                        continue
                
                filtered_records.append(fields)
            
            logger.info(f"Found {len(filtered_records)} records after filtering")
            
            # Tính toán thống kê
            return self._calculate_daily_statistics(filtered_records)
            
        except Exception as e:
            logger.error(f"Error getting daily report: {e}")
            return self._empty_report_data()

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
                
                # From depot
                from_id = fields.get('ID kho đi')
                from_name = fields.get('Kho đi')
                if from_id and from_name and from_id not in depots:
                    depots[from_id] = from_name
                
                # To depot
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
        """Tính toán thống kê từ danh sách records"""
        if not records:
            return self._empty_report_data()
        
        transport_stats = defaultdict(lambda: {'count': 0, 'quantity': 0})
        route_stats = defaultdict(lambda: {'count': 0, 'quantity': 0, 'transport_providers': set()})
        
        total_quantity = 0
        
        for fields in records:
            # Số lượng bao/tải
            quantity = 0
            quantity_field = (fields.get('Số lượng bao/tải giao') or 
                             fields.get('SoLuongBaoTaiGiao') or 
                             fields.get('HandoverQuantity') or 
                             fields.get('Quantity', 0))
            
            try:
                if isinstance(quantity_field, str):
                    quantity = int(quantity_field) if quantity_field.isdigit() else 0
                elif isinstance(quantity_field, (int, float)):
                    quantity = int(quantity_field)
                total_quantity += quantity
            except (ValueError, TypeError):
                pass
            
            # Đơn vị vận chuyển
            transport_provider = (fields.get('Đơn vị vận chuyển') or 
                                 fields.get('DonViVanChuyen') or 
                                 fields.get('TransportProvider') or 
                                 'Không rõ').strip()
            
            if transport_provider:
                transport_stats[transport_provider]['count'] += 1
                transport_stats[transport_provider]['quantity'] += quantity
            
            # Route (kho đi → kho đến)
            from_depot = (fields.get('Kho đi') or 
                         fields.get('KhoDi') or 
                         fields.get('FromDepot') or 
                         'Không rõ').strip()
            
            to_depot = (fields.get('Kho đến') or 
                       fields.get('KhoDen') or 
                       fields.get('ToDepot') or 
                       'Không rõ').strip()
            
            route_key = f"{from_depot} → {to_depot}"
            
            route_stats[route_key]['count'] += 1
            route_stats[route_key]['quantity'] += quantity
            if transport_provider:
                route_stats[route_key]['transport_providers'].add(transport_provider)
        
        # Chuyển đổi sang format cho template
        transport_summary = []
        for provider, stats in transport_stats.items():
            transport_summary.append({
                'name': provider,
                'count': stats['count'],
                'quantity': stats['quantity']
            })
        
        route_summary = []
        for route, stats in route_stats.items():
            route_summary.append({
                'route': route,
                'count': stats['count'],
                'quantity': stats['quantity'],
                'transport_providers': list(stats['transport_providers'])
            })
        
        # Sắp xếp theo số lượng giảm dần
        transport_summary.sort(key=lambda x: x['quantity'], reverse=True)
        route_summary.sort(key=lambda x: x['quantity'], reverse=True)
        
        return {
            'total_records': len(records),
            'total_quantity': total_quantity,
            'transport_providers': dict(transport_stats),
            'routes': dict(route_stats),
            'transport_summary': transport_summary,
            'route_summary': route_summary
        }
