import json
import zipfile
import io
from django.core.files.base import ContentFile

class JsonZipService:
    @staticmethod
    def _gerar_zip_interno(json_data, nome_arquivo_interno="dados.json"):
        """Método privado para centralizar a lógica de minificação e criação do buffer ZIP."""
        # Se for string, valida e minifica. Se for dicionário, dumps.
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
            
        json_minificado = json.dumps(json_data, separators=(',', ':'))
        
        buffer_memoria = io.BytesIO()
        with zipfile.ZipFile(buffer_memoria, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(nome_arquivo_interno, json_minificado)
            
        buffer_memoria.seek(0)
        return buffer_memoria

    @staticmethod
    def compactar_json_para_zip(json_data, nome_arquivo_interno="dados.json"):
        """
        Retorna um objeto ContentFile do Django com o JSON compactado em ZIP.
        Ideal para salvar em FileField.
        """
        buffer = JsonZipService._gerar_zip_interno(json_data, nome_arquivo_interno)
        nome_zip = nome_arquivo_interno.replace('.json', '.zip')
        return ContentFile(buffer.read(), name=nome_zip)

    @staticmethod
    def compactar_json_para_bytes(json_data, nome_arquivo_interno="dados.json"):
        """
        Retorna os bytes puros do ZIP compactado.
        Ideal para salvar em BinaryField ou enviar via rede.
        """
        buffer = JsonZipService._gerar_zip_interno(json_data, nome_arquivo_interno)
        return buffer.getvalue()

    @staticmethod
    def descompactar_zip_para_json(campo_arquivo_ou_bytes, nome_arquivo_interno="dados.json"):
        """
        Lê um ZIP (bytes ou FileField) e retorna o dicionário JSON original.
        """
        if not campo_arquivo_ou_bytes:
            return None
            
        # Normaliza a entrada para bytes
        if isinstance(campo_arquivo_ou_bytes, (bytes, bytearray, memoryview)):
            conteudo_zip = bytes(campo_arquivo_ou_bytes)
        else:
            if not getattr(campo_arquivo_ou_bytes, 'name', None):
                return None
            campo_arquivo_ou_bytes.open(mode='rb')
            conteudo_zip = campo_arquivo_ou_bytes.read()
            campo_arquivo_ou_bytes.close()
            
        buffer_memoria = io.BytesIO(conteudo_zip)
        
        with zipfile.ZipFile(buffer_memoria, mode="r") as zf:
            json_extraido_str = zf.read(nome_arquivo_interno).decode('utf-8')
            
        return json.loads(json_extraido_str)
