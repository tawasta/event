from odoo.tools.translate import TranslationImporter, get_po_paths

MODULE_NAME = "website_event_wording_koulutus"


def post_init_hook(env):
    """Force-apply this module's Finnish translations over website_event's
    own, already-installed ones.

    Odoo's normal translation loading (ir.module.module._update_translations,
    called for every module on install/update) keeps any translation that
    already exists in the database and only fills in missing ones - see
    odoo.tools.translate.TranslationImporter.save(). Since website_event is
    installed first and already provides a Finnish translation for every
    term this module overrides, the normal load would silently keep
    website_event's wording. force_overwrite=True bypasses that and applies
    this module's po file unconditionally.
    """
    importer = TranslationImporter(env.cr, verbose=False)
    for po_path in get_po_paths(MODULE_NAME, "fi_FI"):
        importer.load_file(po_path, "fi_FI")
    importer.save(force_overwrite=True)
