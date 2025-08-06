# FILE: app.py


import streamlit as st
import datetime
import time
from src.styles.material_ui import load_material_ui_css
from src.utils.api import fetch_imex_details
from src.utils.larkbase import (
    larkbase_find_by_field,
    larkbase_write_data,
    larkbase_update_data,
    larkbase_delete_record,
)
from src.utils.config import (
    LARKBASE_FIELDS, API_FIELDS,
    CREATABLE_FIELDS, UPDATABLE_FIELDS, LOCK_FIELDS
)


APP_TOKEN = "Rm9PbvKLeaFFZcsSQpElnRjIgXg"
TABLE_ID = "tblJJPUEFhsXHaxY"


# --- Helper Functions (Không thay đổi) ---
def get_current_timestamp_ms():
    return int(time.time() * 1000)


def convert_date_string_to_ms(date_string: str) -> int | None:
    if not date_string or not isinstance(date_string, str):
        return None
    try:
        dt_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return int(dt_obj.timestamp() * 1000)
    except ValueError:
        return None


def format_timestamp_ms_to_string(ts_ms) -> str:
    if not ts_ms:
        return ""
    try:
        return datetime.datetime.fromtimestamp(int(ts_ms) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return str(ts_ms)


# --- Callback functions để xử lý form submissions ---


def handle_success(message: str):
    """Đặt thông báo thành công và reset ô nhập liệu."""
    st.session_state.last_success_message = message
    # Gán lại giá trị cho widget trong session state, đây là cách làm đúng trong callback
    st.session_state.bill_id_input = ""


def handle_update(record_id, original_bill_id):
    """Callback cho nút 'Lưu chỉnh sửa'."""
    update_data = {}
    date_fields = ["Ngày nhận hàng"]
    numeric_fields = ["Số lượng bao/tải giao", "Số lượng bao tải nhận", "Thiếu thừa bao"]

    # Lấy dữ liệu đã sửa từ các widget trong form thông qua st.session_state
    for col in UPDATABLE_FIELDS:
        key = f"update_{col}"
        if key in st.session_state:
            val = st.session_state[key]
            if col in date_fields and val is not None:
                dt_obj = datetime.datetime.combine(val, datetime.datetime.min.time())
                update_data[col] = int(dt_obj.timestamp() * 1000)
            elif val is not None:
                 update_data[col] = val

    if not update_data:
        st.warning("Không có thay đổi nào để lưu.")
        return

    result = larkbase_update_data(APP_TOKEN, TABLE_ID, record_id, update_data)
    if result:
        handle_success(f"📝 Cập nhật thành công cho Bill ID: {original_bill_id}. Giao diện đã được reset.")
    else:
        st.error("❌ Lỗi khi cập nhật dữ liệu!")


def handle_delete(record_id, original_bill_id):
    """Callback cho nút 'Xóa Bill này' với logic kiểm tra lại trước khi xóa."""
    # 1. Tải lại dữ liệu mới nhất của record từ Larkbase để đảm bảo không có gì thay đổi
    st.info("Đang kiểm tra lại trạng thái record trước khi xóa...")
    latest_record = larkbase_find_by_field(APP_TOKEN, TABLE_ID, "ID", original_bill_id)

    if not latest_record:
        st.error(f"❌ Không tìm thấy record với Bill ID: {original_bill_id}. Có thể đã bị người khác xóa.")
        # Xóa thông báo info
        st.empty()
        return

    # 2. Kiểm tra lại điều kiện khóa trên dữ liệu mới nhất
    fields = latest_record.get("fields", {})
    has_lock_values = any(fields.get(f) for f in LOCK_FIELDS)

    # 3. Nếu bị khóa, báo lỗi và dừng lại
    if has_lock_values:
        locked_fields_found = [f for f in LOCK_FIELDS if fields.get(f)]
        st.error(
            f"❌ Không thể xóa! Record đã được cập nhật bởi người khác và bị khóa bởi các trường: "
            f"{', '.join(locked_fields_found)}. Vui lòng tải lại trang."
        )
        # Xóa thông báo info
        st.empty()
        return

    # 4. Nếu không bị khóa, tiến hành xóa
    result = larkbase_delete_record(APP_TOKEN, TABLE_ID, record_id)
    if result:
        handle_success(f"🗑️ Đã xóa thành công Bill ID: {original_bill_id}. Giao diện đã được reset.")
    else:
        st.error("❌ Xóa không thành công!")


def handle_create(api_data, original_bill_id):
    """Callback cho nút 'Thêm mới vào Larkbase'."""
    new_fields = {}
    # Lấy dữ liệu từ các widget trong form
    for col in CREATABLE_FIELDS:
        key = f"add_{col}"
        if key in st.session_state:
            new_fields[col] = st.session_state[key]

    # Thêm các trường tự động tạo
    new_fields["ID"] = api_data['ID']
    new_fields["Ngày bàn giao"] = get_current_timestamp_ms()

    record_data = {**new_fields, **api_data}
    final_record_data = {k: v for k, v in record_data.items() if v is not None and str(v) != ""}

    try:
        ok = larkbase_write_data(APP_TOKEN, TABLE_ID, final_record_data)
        if ok:
            # Lấy thông tin đã nhập để hiển thị trong thông báo
            so_luong_giao = new_fields.get("Số lượng bao/tải giao", "không có")
            nguoi_ban_giao = new_fields.get("Người bàn giao", "không có")

            # Tạo chuỗi thông báo mới
            success_message = (
                f"✅ Đã thêm thành công Bill ID: {original_bill_id}. "
                f"Số lượng bao/tải giao: {so_luong_giao}. "
                f"Người bàn giao: '{nguoi_ban_giao}'."
            )
            handle_success(success_message)
        else:
            st.error("❌ Không thể thêm mới. Kiểm tra lại thông báo lỗi từ API bên trên nếu có.")
    except Exception as e:
        st.error(f"Lỗi khi ghi dữ liệu: {e}")



# --- Streamlit App UI ---
st.set_page_config(layout="centered")


# Khởi tạo session state nếu chưa tồn tại
if 'last_success_message' not in st.session_state:
    st.session_state.last_success_message = None
if 'bill_id_input' not in st.session_state:
    st.session_state.bill_id_input = ""


load_material_ui_css()
st.markdown(
    '<div style="text-align:center;"><h2>📦 Phân phối giao nhận IMEX</h2>'
    '<p style="color:#1976d2"><b>Nhập Bill ID, tra cứu, thêm, sửa, xóa thông tin giao nhận</b></p></div>',
    unsafe_allow_html=True,
)


# Hiển thị thông báo thành công (nếu có) và xóa đi
if st.session_state.last_success_message:
    st.success(st.session_state.last_success_message)
    st.session_state.last_success_message = None


# Giá trị của widget giờ sẽ được điều khiển bởi các hàm callback
bill_id = st.text_input(
    "Nhập Bill ID:",
    placeholder="Nhập mã Bill ID giao nhận",
    key="bill_id_input"
).strip()


if bill_id:
    record = larkbase_find_by_field(APP_TOKEN, TABLE_ID, "ID", bill_id)


    # --- RECORD EXISTS: VIEW / UPDATE / DELETE ---
    if record:
        fields = record.get("fields", {})
        st.markdown(f"<b>Đã tồn tại thông tin Bill ID <span style='color: #1976d2'>{bill_id}</span>!</b>", unsafe_allow_html=True)

        has_lock_values = any(fields.get(f) for f in LOCK_FIELDS)
        numeric_fields = ["Số lượng bao/tải giao", "Số lượng bao tải nhận", "Thiếu thừa bao"]
        date_fields = ["Ngày nhận hàng"]

        with st.form("update_or_delete"):
            for col in LARKBASE_FIELDS:
                val = fields.get(col, "")
                is_editable = (col in UPDATABLE_FIELDS) and not (col in LOCK_FIELDS and val)

                if not is_editable:
                    display_val = format_timestamp_ms_to_string(val) if col in date_fields or col == "Ngày bàn giao" else val
                    st.text_input(col, display_val, key=f"readonly_{col}", disabled=True)
                else:
                    if col in numeric_fields:
                        default_val = int(val) if val else 0
                        st.number_input(col, key=f"update_{col}", step=1, value=default_val, format="%d")
                    elif col in date_fields:
                        default_val = datetime.datetime.fromtimestamp(int(val) / 1000).date() if val else None
                        st.date_input(col, key=f"update_{col}", value=default_val)
                    else:
                        st.text_input(col, val, key=f"update_{col}")

            col1, col2 = st.columns(2)
            with col1:
                st.form_submit_button(
                    "Lưu chỉnh sửa",
                    on_click=handle_update,
                    args=(record["record_id"], bill_id),
                    use_container_width=True
                )

            can_delete = not has_lock_values
            with col2:
                st.form_submit_button(
                    "Xóa Bill này",
                    disabled=not can_delete,
                    type="secondary",
                    on_click=handle_delete,
                    args=(record["record_id"], bill_id),
                    use_container_width=True
                )

            if not can_delete:
                st.info(f"Lưu ý: Bill này không thể xóa vì đã có thông tin ở một trong các trường sau: {', '.join(LOCK_FIELDS)}. Do đó, nút xóa đã được vô hiệu hóa.")


    # --- RECORD NOT FOUND: CREATE NEW ---
    else:
        st.info(f"Đang tự động tra cứu và thêm mới Bill ID: {bill_id}...")

        with st.spinner("Đang tải dữ liệu từ API..."):
            imex_items = fetch_imex_details(bill_id)

        if not imex_items:
            st.error("❌ Không lấy được dữ liệu chi tiết, kiểm tra lại Bill ID.")
        else:
            example_item = imex_items[0]
            api_data = {
                "ID": bill_id, "Kho đi": example_item.get("fromDepotId", ""), "Kho đến": example_item.get("toDepotId", ""),
                "Số lượng": int(example_item.get("realQuantity") or 0), "Số lượng sản phẩm yêu cầu": int(example_item.get("requiredQuantity") or 0),
                "Số lượng sản phẩm hỏng": int(example_item.get("damagedQuantity") or 0), "Số lượng sản phẩm yêu cầu được duyệt": int(example_item.get("approvedQuantity") or 0),
                "Số lượng sản phẩm yêu cầu được xác nhận": int(example_item.get("realQuantity") or 0), "Ngày tạo": convert_date_string_to_ms(example_item.get("requiredAt", "")),
                "Ngày duyệt": convert_date_string_to_ms(example_item.get("approvedAt", "")), "Ngày xác nhận": convert_date_string_to_ms(example_item.get("confirmedAt", "")),
                "Người xác nhận": example_item.get("approvedByUser", ""),
            }

            with st.form("create_new"):
                numeric_fields = ["Số lượng bao/tải giao"]

                for col in LARKBASE_FIELDS:
                    is_creatable = col in CREATABLE_FIELDS
                    if is_creatable:
                        if col in numeric_fields:
                            st.number_input(col, key=f"add_{col}", step=1, value=0, format="%d")
                        else:
                            st.text_input(col, "", key=f"add_{col}")
                    else:
                        if col == "ID":
                            st.text_input(col, api_data['ID'], key=f"add_{col}_disabled", disabled=True)
                        elif col == "Ngày bàn giao":
                            ts_ms = get_current_timestamp_ms()
                            st.text_input(col, format_timestamp_ms_to_string(ts_ms), key=f"add_{col}_disabled", disabled=True)
                        else:
                            st.text_input(col, "", key=f"add_{col}_disabled", disabled=True, help="Trường này sẽ được nhập ở bước cập nhật sau.")

                st.form_submit_button(
                    "Thêm mới vào Larkbase",
                    on_click=handle_create,
                    args=(api_data, bill_id),
                    use_container_width=True
                )
