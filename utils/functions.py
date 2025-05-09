import json

def convert_json_string_to_dict(json_string: str) -> dict:
  """
  Mengonversi string berformat JSON menjadi dictionary Python.

  Args:
    json_string: String input yang berisi data dalam format JSON.

  Returns:
    Sebuah dictionary Python hasil parsing dari string JSON.
    Mengembalikan dictionary kosong dan mencetak error jika string bukan JSON yang valid.
  """
  try:
    data = json.loads(json_string)
    return data
  except json.JSONDecodeError as e:
    print(f"Error decoding JSON string: {e}")
    return {}
  except TypeError as e:
    print(f"Input must be a string: {e}")
    return {}

def remove_json_wrapper(text):
    if text.startswith("```json"):
        text = text[len("```json"):].lstrip()
    if text.endswith("```"):
        text = text[:-len("```")].rstrip()
    return text
