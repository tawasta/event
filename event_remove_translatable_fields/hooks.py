from odoo.tools import sql

# Fields that this module makes non-translatable
UNTRANSLATED_FIELDS = {
    "event.type": ["name"],
    "event.event": ["name", "description"],
    "event.type.ticket": ["name", "description"],
    "event.event.ticket": ["name", "description"],
}


def post_init_hook(env):
    """Convert the columns of the fields that were translated before the install.

    Odoo converts the jsonb column of a field that stops being translatable only
    on the next update of the module. Until then the values are read as
    dictionaries, which breaks the event forms and the mail scheduler.
    """
    for model_name, field_names in UNTRANSLATED_FIELDS.items():
        model = env[model_name]
        columns = sql.table_columns(env.cr, model._table)
        for field_name in field_names:
            column = columns.get(field_name)
            if not column or column["udt_name"] != "jsonb":
                continue
            field = model._fields[field_name]
            sql.convert_column_translatable(
                env.cr, model._table, field_name, field._column_type[1]
            )
        model.invalidate_model(field_names)
