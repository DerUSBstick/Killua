import contextlib
from typing import Any
from pathlib import Path
from yaml import safe_load
from discord import Locale, app_commands
from logging import info, debug

from killua.static.enums import PrintColors
from killua.static.constants import L10N_PATH, SOURCE_LANG

def gen_string_key(string: str) -> str:
    return string.replace(" ", "_").replace(",", "").replace(".", "").replace("-", "_").lower()

class Translator:
    def __init__(self):
        self._localization_dict: dict[str, dict[str, str]] = {}
        self.load_l10n_files()
    
    def load_l10n_files(self) -> None:
        for filepath in L10N_PATH.glob("*.yaml"):
            print(f"{PrintColors.OKBLUE}Loading localization file: {filepath.stem}{PrintColors.ENDC}")
            if not filepath.exists():
                continue
            lang = filepath.stem
            self._localization_dict[lang] = self.read_yaml(filepath)
    
    def read_yaml(self, filepath: Path):
        with open(filepath, "r", encoding="utf-8") as file:
            yaml_data = safe_load(file)
        if not isinstance(yaml_data, dict):
            raise ValueError(f"Invalid YAML format in {filepath}. Expected a dictionary.")
        return yaml_data
            
    
    def _translate_extras(self, extras: dict[str, Any], locale: Locale) -> dict[str, Any]:
        extras_: dict[str, Any] = {}
        for k, v in extras.items():
            if k == "key":
                continue
            if isinstance(v, app_commands.locale_str):
                extras_[k] = self.translate(v, locale)
            elif isinstance(v, list) and isinstance(v[0], app_commands.locale_str):
                extras_[k] = "/".join([self.translate(i, locale) for i in v])
            else:
                extras_[k] = v
        return extras_

    @staticmethod
    def _get_string_key(string: app_commands.locale_str) -> str:
        if string.extras.get("key") is not None:
            return string.extras.get("key")
        return gen_string_key(string.message)

    def translate(self, string: app_commands.locale_str | str, locale: Locale):
        if isinstance(string, str):
            return string
        
        extras = self._translate_extras(string.extras, locale)
        string_key = self._get_string_key(string)
        print(f"{PrintColors.OKCYAN}Translating string: {string_key} for locale: {locale}{PrintColors.ENDC}")

        source_string = self._localization_dict[SOURCE_LANG].get(string_key)
        if string.extras.get("key") is not None and source_string is None:
            raise ValueError(f"String '{string_key}' not found in source language '{SOURCE_LANG}'.")

        translation = self._localization_dict.get(locale.value, {}).get(string_key)

        translation = translation or source_string or string.message or string_key

        with contextlib.suppress(KeyError):
            translation = translation.format(**extras)
        
        return translation
    
class AppCommandTranslator(app_commands.Translator):
    def __init__(self) -> None:
        super().__init__()

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: Locale,
        context: app_commands.TranslationContext,
    ) -> str:
        print(f"{PrintColors.OKCYAN}Translating app command string: {string.extras.get('key')} / string {string.message} for locale: {locale}{PrintColors.ENDC}")
        if (key := string.extras.get("key")) is None:
            return string.message
        return translator.translate(string, locale)

translator = Translator()