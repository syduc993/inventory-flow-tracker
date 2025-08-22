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

#     def get_daily_report(self, user_id=None, date_str=None, employee_filter=None, from_depot_filter=None, to_depot_filter=None):
#         """Lấy báo cáo hàng ngày - có thể lọc theo nhiều tiêu chí"""
#         try:
#             # Parse date
#             if date_str:
#                 report_date = datetime.strptime(date_str, '%Y-%m-%d')
#                 start_timestamp = int(report_date.timestamp() * 1000)
#                 end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
#             else:
#                 # Lấy tất cả nếu không có date
#                 start_timestamp = 0
#                 end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
#             # Lấy tất cả records
#             all_records = larkbase_get_all(self.app_token, self.table_id)
            
#             # Filter records
#             filtered_records = []
#             for record in all_records:
#                 fields = record.get('fields', {})
                
#                 # Filter by date nếu có
#                 if date_str:
#                     handover_date = fields.get('Ngày bàn giao')
#                     if handover_date:
#                         try:
#                             handover_timestamp = int(handover_date)
#                             if not (start_timestamp <= handover_timestamp < end_timestamp):
#                                 continue
#                         except (ValueError, TypeError):
#                             continue
                
#                 # Filter by employee nếu có
#                 if employee_filter:
#                     record_employee_id = fields.get('ID người bàn giao', '')
#                     if record_employee_id != employee_filter:
#                         continue
                
#                 # Filter by from depot nếu có
#                 if from_depot_filter:
#                     from_depot_id = fields.get('ID kho đi', '')
#                     if from_depot_id != from_depot_filter:
#                         continue
                
#                 # Filter by to depot nếu có
#                 if to_depot_filter:
#                     to_depot_id = fields.get('ID kho đến', '')
#                     if to_depot_id != to_depot_filter:
#                         continue
                
#                 filtered_records.append(fields)
            
#             logger.info(f"Found {len(filtered_records)} records after filtering")
            
#             # Tính toán thống kê
#             return self._calculate_daily_statistics(filtered_records)
            
#         except Exception as e:
#             logger.error(f"Error getting daily report: {e}")
#             return self._empty_report_data()

#     def get_all_employees(self):
#         """Lấy danh sách tất cả nhân viên từ records"""
#         try:
#             all_records = larkbase_get_all(self.app_token, self.table_id)
#             employees = {}
            
#             for record in all_records:
#                 fields = record.get('fields', {})
#                 emp_id = fields.get('ID người bàn giao')
#                 emp_name = fields.get('Người bàn giao')
                
#                 if emp_id and emp_name and emp_id not in employees:
#                     employees[emp_id] = emp_name
            
#             return [{'id': emp_id, 'name': emp_name} for emp_id, emp_name in employees.items()]
#         except Exception as e:
#             logger.error(f"Error getting employees: {e}")
#             return []

#     def get_all_depots(self):
#         """Lấy danh sách tất cả depots từ records"""
#         try:
#             all_records = larkbase_get_all(self.app_token, self.table_id)
#             depots = {}
            
#             for record in all_records:
#                 fields = record.get('fields', {})
                
#                 # From depot
#                 from_id = fields.get('ID kho đi')
#                 from_name = fields.get('Kho đi')
#                 if from_id and from_name and from_id not in depots:
#                     depots[from_id] = from_name
                
#                 # To depot
#                 to_id = fields.get('ID kho đến')
#                 to_name = fields.get('Kho đến')
#                 if to_id and to_name and to_id not in depots:
#                     depots[to_id] = to_name
            
#             return [{'id': depot_id, 'name': depot_name} for depot_id, depot_name in depots.items()]
#         except Exception as e:
#             logger.error(f"Error getting depots: {e}")
#             return []

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
#             return self._empty_report_data()
        
#         transport_stats = defaultdict(lambda: {'count': 0, 'quantity': 0})
#         route_stats = defaultdict(lambda: {'count': 0, 'quantity': 0, 'transport_providers': set()})
        
#         total_quantity = 0
        
#         for fields in records:
#             # Số lượng bao/tải
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
#                 pass
            
#             # Đơn vị vận chuyển
#             transport_provider = (fields.get('Đơn vị vận chuyển') or 
#                                  fields.get('DonViVanChuyen') or 
#                                  fields.get('TransportProvider') or 
#                                  'Không rõ').strip()
            
#             if transport_provider:
#                 transport_stats[transport_provider]['count'] += 1
#                 transport_stats[transport_provider]['quantity'] += quantity
            
#             # Route (kho đi → kho đến)
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

#     def export_route_records_to_excel(self, from_depot, to_depot, user_id=None, date_str=None, employee_filter=None):
#         """Xuất records của một tuyến đường cụ thể ra Excel"""
#         try:
#             from openpyxl import Workbook
#             from openpyxl.styles import Font, PatternFill, Alignment
#             from datetime import datetime, timedelta
#             import io
            
#             # Lấy dữ liệu báo cáo theo filters
#             if date_str:
#                 report_date = datetime.strptime(date_str, '%Y-%m-%d')
#                 start_timestamp = int(report_date.timestamp() * 1000)
#                 end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
#             else:
#                 start_timestamp = 0
#                 end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
#             # Lấy tất cả records
#             all_records = larkbase_get_all(self.app_token, self.table_id)
            
#             # Filter records theo tuyến đường cụ thể
#             route_records = []
#             for record in all_records:
#                 fields = record.get('fields', {})
                
#                 # Filter by date nếu có
#                 if date_str:
#                     handover_date = fields.get('Ngày bàn giao')
#                     if handover_date:
#                         try:
#                             handover_timestamp = int(handover_date)
#                             if not (start_timestamp <= handover_timestamp < end_timestamp):
#                                 continue
#                         except (ValueError, TypeError):
#                             continue
                
#                 # Filter by employee nếu có
#                 if employee_filter:
#                     record_employee_id = fields.get('ID người bàn giao', '')
#                     if record_employee_id != employee_filter:
#                         continue
                
#                 # ✅ QUAN TRỌNG: Filter theo tuyến đường cụ thể
#                 record_from_depot = fields.get('Kho đi', '').strip()
#                 record_to_depot = fields.get('Kho đến', '').strip()
                
#                 if record_from_depot == from_depot and record_to_depot == to_depot:
#                     route_records.append(fields)
            
#             if not route_records:
#                 return None, 0
            
#             # Tạo workbook
#             wb = Workbook()
#             ws = wb.active
#             ws.title = f"{from_depot} → {to_depot}"
            
#             # Header style
#             header_font = Font(bold=True, color="FFFFFF")
#             header_fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
#             header_alignment = Alignment(horizontal="center", vertical="center")
            
#             # Set headers
#             headers = ["ID", "Số lượng bao/tải giao", "ID người bàn giao", "Người bàn giao"]
#             for col, header in enumerate(headers, 1):
#                 cell = ws.cell(row=1, column=col, value=header)
#                 cell.font = header_font
#                 cell.fill = header_fill
#                 cell.alignment = header_alignment
            
#             # Add data
#             for row, fields in enumerate(route_records, 2):
#                 ws.cell(row=row, column=1, value=fields.get('ID', ''))
#                 ws.cell(row=row, column=2, value=fields.get('Số lượng bao/tải giao', 0))
#                 ws.cell(row=row, column=3, value=fields.get('ID người bàn giao', ''))
#                 ws.cell(row=row, column=4, value=fields.get('Người bàn giao', ''))
            
#             # Auto-fit columns
#             for column in ws.columns:
#                 max_length = 0
#                 column_letter = column[0].column_letter
#                 for cell in column:
#                     try:
#                         if len(str(cell.value)) > max_length:
#                             max_length = len(str(cell.value))
#                     except:
#                         pass
#                 adjusted_width = min(max_length + 2, 50)
#                 ws.column_dimensions[column_letter].width = adjusted_width
            
#             # Save to BytesIO
#             excel_buffer = io.BytesIO()
#             wb.save(excel_buffer)
#             excel_buffer.seek(0)
            
#             return excel_buffer, len(route_records)
            
#         except Exception as e:
#             logger.error(f"Error creating route Excel export: {e}")
#             return None, 0

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
        # ✅ THAY ĐỔI: Group theo route + transport provider thay vì chỉ route
        route_transport_stats = defaultdict(lambda: {'count': 0, 'quantity': 0})
        
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
            
            # ✅ THAY ĐỔI: Tạo composite key từ route + transport provider
            route_transport_key = f"{route_key}|{transport_provider}"
            
            route_transport_stats[route_transport_key]['count'] += 1
            route_transport_stats[route_transport_key]['quantity'] += quantity
        
        # Chuyển đổi sang format cho template
        transport_summary = []
        for provider, stats in transport_stats.items():
            transport_summary.append({
                'name': provider,
                'count': stats['count'],
                'quantity': stats['quantity']
            })
        
        # ✅ THAY ĐỔI: Tách route và transport provider từ composite key
        route_summary = []
        for route_transport_key, stats in route_transport_stats.items():
            # Tách route và transport provider từ composite key
            route_part, transport_part = route_transport_key.split('|', 1)
            
            route_summary.append({
                'route': route_part,
                'transport_provider': transport_part,
                'count': stats['count'],
                'quantity': stats['quantity']
            })
        
        # Sắp xếp theo số lượng giảm dần
        transport_summary.sort(key=lambda x: x['quantity'], reverse=True)
        route_summary.sort(key=lambda x: x['quantity'], reverse=True)
        
        return {
            'total_records': len(records),
            'total_quantity': total_quantity,
            'transport_providers': dict(transport_stats),
            'routes': dict(route_transport_stats),  # ✅ THAY ĐỔI: Sử dụng route_transport_stats
            'transport_summary': transport_summary,
            'route_summary': route_summary
        }


    def export_route_records_to_excel(self, from_depot, to_depot, user_id=None, date_str=None, employee_filter=None):
        """Xuất records của một tuyến đường cụ thể ra Excel"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            from datetime import datetime, timedelta
            import io
            
            # Lấy dữ liệu báo cáo theo filters
            if date_str:
                report_date = datetime.strptime(date_str, '%Y-%m-%d')
                start_timestamp = int(report_date.timestamp() * 1000)
                end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
            else:
                start_timestamp = 0
                end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
            # Lấy tất cả records
            all_records = larkbase_get_all(self.app_token, self.table_id)
            
            # Filter records theo tuyến đường cụ thể
            route_records = []
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
                
                # ✅ QUAN TRỌNG: Filter theo tuyến đường cụ thể
                record_from_depot = fields.get('Kho đi', '').strip()
                record_to_depot = fields.get('Kho đến', '').strip()
                
                if record_from_depot == from_depot and record_to_depot == to_depot:
                    route_records.append(fields)
            
            if not route_records:
                return None, 0
            
            # Tạo workbook
            wb = Workbook()
            ws = wb.active
            ws.title = f"{from_depot} → {to_depot}"
            
            # Header style
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            # Set headers
            headers = ["ID", "Số lượng bao/tải giao", "ID người bàn giao", "Người bàn giao"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
            
            # Add data
            for row, fields in enumerate(route_records, 2):
                ws.cell(row=row, column=1, value=fields.get('ID', ''))
                ws.cell(row=row, column=2, value=fields.get('Số lượng bao/tải giao', 0))
                ws.cell(row=row, column=3, value=fields.get('ID người bàn giao', ''))
                ws.cell(row=row, column=4, value=fields.get('Người bàn giao', ''))
            
            # Auto-fit columns
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
            
            # Save to BytesIO
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)
            
            return excel_buffer, len(route_records)
            
        except Exception as e:
            logger.error(f"Error creating route Excel export: {e}")
            return None, 0
