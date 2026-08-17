# Finnish strings that come from Python `_()` calls in website_event's own
# code cannot be overridden via a po file (Odoo resolves them by reading
# website_event's own i18n file directly, by module name - see
# odoo.tools.translate.CodeTranslations). These are therefore intercepted
# and swapped at the Python level instead, after website_event's own code
# has already produced the (Finnish) text.
WORDING_REPLACEMENTS = {
    "Tulevat tapahtumat": "Tulevat koulutukset",
    "Menneet tapahtumat": "Menneet koulutukset",
    "Kaikki tapahtumat": "Kaikki koulutukset",
    "Tapahtumat": "Koulutukset",
    "Seuraavat tapahtumat": "Seuraavat koulutukset",
    "Verkkosivuston on oltava saman yrityksen kuin tapahtuma.": (
        "Verkkosivuston on oltava saman yrityksen kuin koulutus."
    ),
    "Kysymystä ei voi yhdistää sekä tapahtumaan että tapahtumatyyppiin.": (
        "Kysymystä ei voi yhdistää sekä koulutukseen että koulutustyyppiin."
    ),
    "Tähän tapahtumaan ei ole enää saatavilla lippuja": (
        "Tähän koulutukseen ei ole enää saatavilla lippuja"
    ),
}
