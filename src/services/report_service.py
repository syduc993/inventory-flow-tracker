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
            if date_str:
                report_date = datetime.strptime(date_str, '%Y-%m-%d')
                start_timestamp = int(report_date.timestamp() * 1000)
                end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
            else:
                start_timestamp = 0
                end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
            all_records = larkbase_get_all(self.app_token, self.table_id)
            
            filtered_records = []
            for record in all_records:
                fields = record.get('fields', {})
                
                if date_str:
                    handover_date = fields.get('Ngày bàn giao')
                    if handover_date:
                        try:
                            handover_timestamp = int(handover_date)
                            if not (start_timestamp <= handover_timestamp < end_timestamp):
                                continue
                        except (ValueError, TypeError):
                            continue
                
                if employee_filter and fields.get('ID người bàn giao', '') != employee_filter:
                    continue
                
                if from_depot_filter and fields.get('ID kho đi', '') != from_depot_filter:
                    continue
                
                if to_depot_filter and fields.get('ID kho đến', '') != to_depot_filter:
                    continue
                
                filtered_records.append(fields)
            
            logger.info(f"Found {len(filtered_records)} records after filtering")
            
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
        """Tính toán thống kê từ danh sách records"""
        if not records:
            return self._empty_report_data()
        
        route_transport_stats = defaultdict(lambda: {'count': 0, 'bags': 0, 'loads': 0})
        total_loads = 0
        
        for fields in records:
            bags = 0
            try:
                bags_field = fields.get('Số lượng bao', 0)
                if isinstance(bags_field, str):
                    bags = int(bags_field) if bags_field.isdigit() else 0
                elif isinstance(bags_field, (int, float)):
                    bags = int(bags_field)
            except (ValueError, TypeError):
                pass
                
            loads = 0
            try:
                loads_field = fields.get('Số lượng tải', fields.get('Số lượng bao/tải giao', 0))
                if isinstance(loads_field, str):
                    loads = int(loads_field) if loads_field.isdigit() else 0
                elif isinstance(loads_field, (int, float)):
                    loads = int(loads_field)
                total_loads += loads
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
        
        # --- Tính toán cho Bảng Tuyến đường ---
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
        
        # === BỔ SUNG: TÍNH TOÁN CHO BẢNG ĐƠN VỊ VẬN CHUYỂN ===
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
        # === KẾT THÚC PHẦN BỔ SUNG ===
        
        return {
            'total_records': len(records),
            'total_quantity': total_loads,
            'routes': dict(route_transport_stats),
            'route_summary': route_summary,
            'transport_providers': dict(transport_stats),
            'transport_summary': transport_summary # Trả về dữ liệu đã được tính toán
        }

    def export_route_records_to_excel(self, from_depot, to_depot, user_id=None, date_str=None, employee_filter=None):
        """Xuất records của một tuyến đường cụ thể ra Excel"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            import io
            
            if date_str:
                report_date = datetime.strptime(date_str, '%Y-%m-%d')
                start_timestamp = int(report_date.timestamp() * 1000)
                end_timestamp = int((report_date + timedelta(days=1)).timestamp() * 1000)
            else:
                start_timestamp = 0
                end_timestamp = int(datetime.now().timestamp() * 1000) + 86400000
            
            all_records = larkbase_get_all(self.app_token, self.table_id)
            
            route_records = []
            for record in all_records:
                fields = record.get('fields', {})
                if date_str:
                    handover_date = fields.get('Ngày bàn giao')
                    if handover_date and not (start_timestamp <= int(handover_date) < end_timestamp):
                        continue
                if employee_filter and fields.get('ID người bàn giao', '') != employee_filter:
                    continue
                if fields.get('Kho đi', '').strip() == from_depot and fields.get('Kho đến', '').strip() == to_depot:
                    route_records.append(fields)
            
            if not route_records: return None, 0
            
            wb = Workbook()
            ws = wb.active
            ws.title = f"{from_depot} → {to_depot}"
            
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            headers = ["ID", "Số lượng bao", "Số lượng tải", "ID người bàn giao", "Người bàn giao"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font, cell.fill, cell.alignment = header_font, header_fill, header_alignment
            
            for row, fields in enumerate(route_records, 2):
                ws.cell(row=row, column=1, value=fields.get('ID', ''))
                ws.cell(row=row, column=2, value=fields.get('Số lượng bao', 0))
                ws.cell(row=row, column=3, value=fields.get('Số lượng tải') or fields.get('Số lượng bao/tải giao', 0))
                ws.cell(row=row, column=4, value=fields.get('ID người bàn giao', ''))
                ws.cell(row=row, column=5, value=fields.get('Người bàn giao', ''))
            
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except: pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)
            return excel_buffer, len(route_records)
            
        except Exception as e:
            logger.error(f"Error creating route Excel export: {e}")
            return None, 0