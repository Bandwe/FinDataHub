# -*- coding: utf-8 -*-
"""
Industry template and industry data services.
"""
from datetime import date, datetime
from io import BytesIO
import re

from sqlalchemy import or_

from models import db, Company, CustomModule, CustomModuleData, ModuleKeyword


SYSTEM_KEYWORDS = {'code', 'name', 'year'}
RESERVED_KEYWORDS = SYSTEM_KEYWORDS | {
    'id', 'module_id', 'company_id', 'company_code', 'company_name',
    'created_at', 'updated_at', 'new_company_name'
}
VALID_DATA_TYPES = {'string', 'number', 'date'}
KEYWORD_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')


class ServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def user_keywords(module):
    return [
        keyword for keyword in sorted(module.keywords, key=lambda item: item.sort_order or 0)
        if keyword.keyword not in SYSTEM_KEYWORDS
    ]


def serialize_template(module):
    return {
        'id': module.id,
        'name': module.name,
        'code': module.code,
        'icon': module.icon,
        'description': module.description,
        'sort_order': module.sort_order,
        'is_active': bool(module.is_active),
        'is_locked': bool(module.is_locked),
        'locked_at': module.locked_at.strftime('%Y-%m-%d %H:%M:%S') if module.locked_at else None,
        'version': module.version or 1,
        'source_module_id': module.source_module_id,
        'created_by': module.created_by,
        'created_at': module.created_at.strftime('%Y-%m-%d %H:%M:%S') if module.created_at else None,
        'updated_at': module.updated_at.strftime('%Y-%m-%d %H:%M:%S') if module.updated_at else None,
        'keywords': [keyword.to_dict() for keyword in user_keywords(module)]
    }


def list_templates(include_inactive=False, locked_only=False):
    query = CustomModule.query
    if not include_inactive:
        query = query.filter_by(is_active=True)
    if locked_only:
        query = query.filter_by(is_locked=True)
    modules = query.order_by(CustomModule.sort_order.asc(), CustomModule.id.asc()).all()
    return [serialize_template(module) for module in modules]


def get_template(module_id):
    module = CustomModule.query.get(module_id)
    if not module:
        raise ServiceError('行业模板不存在', 404)
    return module


def get_template_by_code(code, require_active=True, require_locked=False):
    query = CustomModule.query.filter_by(code=code)
    if require_active:
        query = query.filter_by(is_active=True)
    if require_locked:
        query = query.filter_by(is_locked=True)
    module = query.first()
    if not module:
        raise ServiceError('行业模板不存在或未确认', 404)
    return module


def _validate_base_payload(data, existing=None):
    if not isinstance(data, dict):
        raise ServiceError('请求体必须是JSON对象')
    name = _text_value(data, 'name', '')
    code = _text_value(data, 'code', '')
    if not name:
        raise ServiceError('行业名称不能为空')
    if not existing and not code:
        raise ServiceError('行业代码不能为空')
    if code and not KEYWORD_RE.match(code):
        raise ServiceError('行业代码必须以英文字母开头，只能包含字母、数字和下划线')

    if code:
        duplicate = CustomModule.query.filter_by(code=code).first()
        if duplicate and (not existing or duplicate.id != existing.id):
            raise ServiceError('行业代码已存在')
    return name, code


def _text_value(data, key, default=''):
    value = data.get(key, default)
    if value is None:
        value = default
    if not isinstance(value, str):
        raise ServiceError(f'{key} 必须是字符串')
    return value.strip()


def _boolean_value(data, key, default):
    value = data.get(key, default)
    if type(value) is not bool:
        raise ServiceError(f'{key} 必须是布尔值')
    return value


def _nullable_integer_value(data, key, default=None, minimum=None):
    value = data.get(key, default)
    if value is None:
        return None
    if type(value) is not int:
        raise ServiceError(f'{key} 必须是整数')
    if minimum is not None and value < minimum:
        raise ServiceError(f'{key} 不能小于 {minimum}')
    return value


def _integer_value(data, key, default, minimum=None, maximum=None):
    value = data.get(key, default)
    if type(value) is not int:
        raise ServiceError(f'{key} 必须是整数')
    if minimum is not None and value < minimum:
        raise ServiceError(f'{key} 不能小于 {minimum}')
    if maximum is not None and value > maximum:
        raise ServiceError(f'{key} 不能大于 {maximum}')
    return value


def validate_fields(fields):
    if not isinstance(fields, list):
        raise ServiceError('fields 必须是数组')
    normalized = []
    seen = set()
    for index, raw_field in enumerate(fields or []):
        if not isinstance(raw_field, dict):
            raise ServiceError(f'第{index + 1}个字段格式不正确')
        keyword = _text_value(raw_field, 'keyword', '')
        label = _text_value(raw_field, 'label', '')
        data_type = _text_value(raw_field, 'data_type', 'string')
        is_required = _boolean_value(raw_field, 'is_required', False)
        sort_order = _integer_value(raw_field, 'sort_order', index, 0, 999)

        if not keyword and not label:
            continue
        if not keyword:
            raise ServiceError(f'第{index + 1}个字段的字段代码不能为空')
        if keyword in RESERVED_KEYWORDS:
            raise ServiceError(f'字段代码 {keyword} 是系统保留字段')
        if not KEYWORD_RE.match(keyword):
            raise ServiceError(f'字段代码 {keyword} 必须以英文字母开头，只能包含字母、数字和下划线')
        if keyword in seen:
            raise ServiceError(f'字段代码 {keyword} 重复')
        if not label:
            raise ServiceError(f'字段 {keyword} 的显示名称不能为空')
        if data_type not in VALID_DATA_TYPES:
            raise ServiceError(f'字段 {label} 的数据类型不支持')

        seen.add(keyword)
        normalized.append({
            'keyword': keyword,
            'label': label,
            'data_type': data_type,
            'is_required': is_required,
            'sort_order': sort_order
        })
    return normalized


def replace_template_fields(module, fields):
    normalized_fields = validate_fields(fields)
    ModuleKeyword.query.filter_by(module_id=module.id).delete()
    for index, field in enumerate(normalized_fields):
        db.session.add(ModuleKeyword(
            module_id=module.id,
            keyword=field['keyword'],
            label=field['label'],
            data_type=field['data_type'],
            is_required=field['is_required'],
            sort_order=field.get('sort_order', index)
        ))


def _fields_payload(data):
    if 'fields' in data:
        return data['fields']
    if 'keywords' in data:
        return data['keywords']
    return []


def create_template(data):
    name, code = _validate_base_payload(data)
    module = CustomModule(
        name=name,
        code=code,
        icon=_text_value(data, 'icon', 'Grid') or 'Grid',
        description=_text_value(data, 'description', ''),
        sort_order=_integer_value(data, 'sort_order', 0, 0, 999),
        is_active=_boolean_value(data, 'is_active', True),
        is_locked=False,
        version=_integer_value(data, 'version', 1, 1),
        source_module_id=_nullable_integer_value(data, 'source_module_id', None, 1),
        created_by=_text_value(data, 'created_by', 'admin') or 'admin'
    )
    db.session.add(module)
    db.session.flush()
    replace_template_fields(module, _fields_payload(data))
    db.session.commit()
    return serialize_template(module)


def update_template(module_id, data):
    module = get_template(module_id)
    name, code = _validate_base_payload(data, module)
    if module.is_locked and ('fields' in data or 'keywords' in data):
        raise ServiceError('模板已确认，字段不可修改', 409)

    module.name = name
    if code:
        module.code = code
    if 'icon' in data:
        module.icon = _text_value(data, 'icon', 'Grid') or 'Grid'
    if 'description' in data:
        module.description = _text_value(data, 'description', '')
    if 'sort_order' in data:
        module.sort_order = _integer_value(data, 'sort_order', 0, 0, 999)
    if 'is_active' in data:
        module.is_active = _boolean_value(data, 'is_active', True)

    if not module.is_locked and ('fields' in data or 'keywords' in data):
        replace_template_fields(module, _fields_payload(data))

    db.session.commit()
    return serialize_template(module)


def confirm_template(module_id):
    module = get_template(module_id)
    if module.is_locked:
        return serialize_template(module)
    if not user_keywords(module):
        raise ServiceError('确认模板前至少需要添加一个行业字段')
    module.is_locked = True
    module.locked_at = datetime.now()
    db.session.commit()
    return serialize_template(module)


def _next_clone_code(module, requested_code=None):
    if requested_code:
        return requested_code
    base = f'{module.code}_v{(module.version or 1) + 1}'
    candidate = base
    suffix = 2
    while CustomModule.query.filter_by(code=candidate).first():
        candidate = f'{base}_{suffix}'
        suffix += 1
    return candidate


def clone_template(module_id, data):
    if not isinstance(data, dict):
        raise ServiceError('请求体必须是JSON对象')
    source = get_template(module_id)
    requested_code = _text_value(data, 'code', '') or None
    code = _next_clone_code(source, requested_code)
    name = _text_value(data, 'name', '') or f'{source.name} v{(source.version or 1) + 1}'
    _validate_base_payload({'name': name, 'code': code})

    clone = CustomModule(
        name=name,
        code=code,
        icon=_text_value(data, 'icon', source.icon or 'Grid') or 'Grid',
        description=_text_value(data, 'description', source.description or ''),
        sort_order=_integer_value(data, 'sort_order', source.sort_order or 0, 0, 999),
        is_active=True,
        is_locked=False,
        version=(source.version or 1) + 1,
        source_module_id=source.id,
        created_by=_text_value(data, 'created_by', 'admin') or 'admin'
    )
    db.session.add(clone)
    db.session.flush()
    replace_template_fields(clone, [keyword.to_dict() for keyword in user_keywords(source)])
    db.session.commit()
    return serialize_template(clone)


def delete_or_disable_template(module_id):
    module = get_template(module_id)
    has_data = CustomModuleData.query.filter_by(module_id=module.id).first() is not None
    if has_data and module.is_active:
        module.is_active = False
        db.session.commit()
        return {'deleted': False, 'disabled': True}
    if has_data:
        CustomModuleData.query.filter_by(module_id=module.id).delete(synchronize_session=False)
    db.session.delete(module)
    db.session.commit()
    return {'deleted': True, 'disabled': False}


def make_template_workbook(module):
    import pandas as pd

    columns = ['代码', '个股名称', '年份'] + [keyword.label for keyword in user_keywords(module)]
    sample = ['000001', '示例公司', datetime.now().year]
    for keyword in user_keywords(module):
        if keyword.data_type == 'number':
            sample.append(0)
        elif keyword.data_type == 'date':
            sample.append(datetime.now().strftime('%Y-%m-%d'))
        else:
            sample.append('')

    output = BytesIO()
    pd.DataFrame([sample], columns=columns).to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return output


def _blank(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ''
    try:
        return bool(value != value)
    except (TypeError, ValueError):
        return False


def _cell_text(value):
    return '' if _blank(value) else str(value).strip()


def _parse_year(value):
    if _blank(value):
        raise ServiceError('年份不能为空')
    try:
        year = int(value)
    except (TypeError, ValueError):
        raise ServiceError('年份必须是数字')
    if year < 1900 or year > 2100:
        raise ServiceError('年份必须在 1900 到 2100 之间')
    return year


def _parse_dynamic_value(keyword, value):
    if _blank(value):
        if keyword.is_required:
            raise ServiceError(f'{keyword.label}不能为空')
        return None

    if keyword.data_type == 'number':
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ServiceError(f'{keyword.label}必须是数字')
    if keyword.data_type == 'date':
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        if isinstance(value, date):
            return value.isoformat()
        try:
            return datetime.strptime(str(value), '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            raise ServiceError(f'{keyword.label}必须是 YYYY-MM-DD 格式')
    return str(value).strip()


def _ensure_module_ready(module):
    if not module.is_locked:
        raise ServiceError('行业模板尚未确认，不能录入或导入数据', 409)
    if not module.is_active:
        raise ServiceError('行业模板已停用', 409)


def _dynamic_data_from_payload(module, data, partial=False):
    dynamic_data = {}
    for keyword in user_keywords(module):
        if keyword.keyword in data:
            value = _parse_dynamic_value(keyword, data.get(keyword.keyword))
            if value is not None or partial:
                dynamic_data[keyword.keyword] = value
        elif keyword.is_required and not partial:
            raise ServiceError(f'{keyword.label}不能为空')
    return dynamic_data


def _company_from_payload(data, allow_create=False):
    company_id = data.get('company_id')
    if company_id is not None:
        if type(company_id) is not int or company_id < 1:
            raise ServiceError('company_id 必须是正整数')
        company = Company.query.get(company_id)
        if not company:
            raise ServiceError('公司不存在', 404)
        return company

    company_code = _cell_text(data.get('company_code') or data.get('code'))
    if not company_code:
        raise ServiceError('公司不能为空')

    company = Company.query.filter_by(code=company_code).first()
    if company:
        return company
    if not allow_create:
        raise ServiceError('公司不存在', 404)

    company_name = _cell_text(data.get('company_name') or data.get('name')) or company_code
    company = Company(code=company_code, name=company_name)
    db.session.add(company)
    db.session.flush()
    return company


def _query_integer(args, key, default, minimum=None, maximum=None):
    raw_value = args.get(key)
    if raw_value in (None, ''):
        return default
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ServiceError(f'{key} 必须是整数') from exc
    if minimum is not None and value < minimum:
        raise ServiceError(f'{key} 不能小于 {minimum}')
    if maximum is not None and value > maximum:
        raise ServiceError(f'{key} 不能大于 {maximum}')
    return value


def list_industry_data(module_code, args):
    module = get_template_by_code(module_code, require_locked=True)
    page = _query_integer(args, 'page', 1, 1)
    per_page = _query_integer(args, 'per_page', 20, 1, 500)
    keyword = args.get('keyword', '')

    query = CustomModuleData.query.filter_by(module_id=module.id)
    if keyword:
        query = query.join(Company).filter(or_(
            Company.name.contains(keyword),
            Company.code.contains(keyword)
        ))
    pagination = query.order_by(CustomModuleData.year.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }


def create_industry_record(module_code, data):
    module = get_template_by_code(module_code, require_locked=False)
    _ensure_module_ready(module)
    company = _company_from_payload(data, allow_create=True)
    year = _parse_year(data.get('year'))

    existing = CustomModuleData.query.filter_by(
        module_id=module.id, company_id=company.id, year=year
    ).first()
    if existing:
        raise ServiceError('该公司该年份的记录已存在')

    record = CustomModuleData(
        module_id=module.id,
        company_id=company.id,
        year=year,
        data=_dynamic_data_from_payload(module, data)
    )
    db.session.add(record)
    db.session.commit()
    return record.to_dict()


def update_industry_record(module_code, record_id, data):
    module = get_template_by_code(module_code, require_locked=True)
    _ensure_module_ready(module)
    record = CustomModuleData.query.filter_by(id=record_id, module_id=module.id).first()
    if not record:
        raise ServiceError('记录不存在', 404)

    if 'company_id' in data or 'company_code' in data or 'code' in data:
        record.company_id = _company_from_payload(data, allow_create=True).id
    if 'year' in data:
        record.year = _parse_year(data.get('year'))

    duplicate = CustomModuleData.query.filter_by(
        module_id=module.id, company_id=record.company_id, year=record.year
    ).first()
    if duplicate and duplicate.id != record.id:
        raise ServiceError('该公司该年份的记录已存在')

    dynamic_data = dict(record.data or {})
    dynamic_data.update(_dynamic_data_from_payload(module, data, partial=True))
    record.data = dynamic_data
    db.session.commit()
    return record.to_dict()


def delete_industry_record(module_code, record_id):
    module = get_template_by_code(module_code, require_locked=True)
    record = CustomModuleData.query.filter_by(id=record_id, module_id=module.id).first()
    if not record:
        raise ServiceError('记录不存在', 404)
    db.session.delete(record)
    db.session.commit()


def export_industry_data(module_code):
    import pandas as pd

    module = get_template_by_code(module_code, require_locked=True)
    records = CustomModuleData.query.filter_by(module_id=module.id).all()
    if not records:
        raise ServiceError('没有数据可导出')

    rows = []
    for record in records:
        item = record.to_dict()
        row = {
            '代码': item.get('company_code'),
            '个股名称': item.get('company_name'),
            '年份': item.get('year')
        }
        for keyword in user_keywords(module):
            row[keyword.label] = item.get(keyword.keyword)
        rows.append(row)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(rows).to_excel(writer, index=False, sheet_name=module.name[:31])
    output.seek(0)
    return output


def import_industry_data(module_code, file_storage):
    import pandas as pd

    module = get_template_by_code(module_code, require_locked=False)
    _ensure_module_ready(module)
    if not file_storage or not file_storage.filename:
        raise ServiceError('请选择文件')

    df = pd.read_excel(file_storage)
    label_to_keyword = {keyword.label: keyword for keyword in user_keywords(module)}
    errors = []
    success_count = 0

    for index, row in df.iterrows():
        try:
            company_code = _cell_text(row.get('代码'))
            company_name = _cell_text(row.get('个股名称'))
            year = _parse_year(row.get('年份'))
            if not company_code:
                raise ServiceError('代码不能为空')
            if not company_name:
                company_name = company_code

            company = Company.query.filter_by(code=company_code).first()
            if not company:
                company = Company(code=company_code, name=company_name)
                db.session.add(company)
                db.session.flush()

            payload = {}
            for label, keyword in label_to_keyword.items():
                if label in row:
                    payload[keyword.keyword] = row.get(label)
            dynamic_data = _dynamic_data_from_payload(module, payload)

            existing = CustomModuleData.query.filter_by(
                module_id=module.id, company_id=company.id, year=year
            ).first()
            if existing:
                existing.data = dynamic_data
            else:
                db.session.add(CustomModuleData(
                    module_id=module.id,
                    company_id=company.id,
                    year=year,
                    data=dynamic_data
                ))
            success_count += 1
        except ServiceError as exc:
            errors.append(f'第{index + 2}行: {exc.message}')
        except Exception as exc:
            errors.append(f'第{index + 2}行: {str(exc)}')

    db.session.commit()
    return {
        'success': success_count,
        'error': len(errors),
        'errors': errors
    }


def compare_industry_data(module_code, data):
    module = get_template_by_code(module_code, require_locked=True)
    company_ids = data.get('company_ids') or []
    years = data.get('years') or []
    metric = data.get('metric') or ''
    if not isinstance(company_ids, list) or any(type(item) is not int or item < 1 for item in company_ids):
        raise ServiceError('company_ids 必须是正整数数组')
    if not isinstance(years, list) or any(type(item) is not int for item in years):
        raise ServiceError('years 必须是整数数组')
    if not isinstance(metric, str):
        raise ServiceError('metric 必须是字符串')
    if not company_ids or not years or not metric:
        raise ServiceError('参数不完整')
    if metric not in {keyword.keyword for keyword in user_keywords(module)}:
        raise ServiceError('指标不存在')

    records = CustomModuleData.query.filter(
        CustomModuleData.module_id == module.id,
        CustomModuleData.company_id.in_(company_ids),
        CustomModuleData.year.in_(years)
    ).all()

    company_data = {}
    for record in records:
        company_name = record.company.name if record.company else '未知'
        company_data.setdefault(company_name, []).append({
            'year': record.year,
            'value': (record.data or {}).get(metric)
        })
    return company_data
