import base64
import json

import nameko
import requests
from Crypto.Cipher import DES3
from Crypto.Hash import MD5, SHA1
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util.Padding import pad

from nameko.extensions import DependencyProvider

ENCODING = "utf-8"
PAD_STYLE = "pkcs7"
SIGNATURE_ALGORITHM = "SHA1withRSA"


class XHJClient:
    def __init__(self, config):
        self.config = config
        self.xhj = self.config.get("XHJ", {})
        self.private_key = self.xhj.get("PRIVATE_KEY")
        self.public_key = self.xhj.get("PUBLIC_KEY")
        self.des_key = self.xhj.get("DES_KEY")
        self.base_url = self.xhj.get("API_BASE_URL")
        self.mchnt_num = self.xhj.get("MCHNT_NUM")

    @staticmethod
    def format_before_sign(params):
        values = [str(params[i]) for i in sorted(params) if i]
        return "|".join(values)

    def sign(self, text):
        format_text = self.format_before_sign(text)
        pri_key = RSA.importKey(self.private_key)
        signer = PKCS1_v1_5.new(pri_key)
        hash_obj = SHA1.new(format_text.encode(ENCODING))
        return base64.b64encode(signer.sign(hash_obj)).decode("utf8")

    def verify(self, decrypt_cipher, signature):
        clear_str = json.dumps(decrypt_cipher)
        pub = RSA.importKey(self.public_key)
        h = MD5.new(clear_str.encode('utf-8'))
        verifier = PKCS1_v1_5.new(pub)
        return verifier.verify(h, base64.b64decode(signature))

    def encode_des3(self, text):
        key = self.des_key[:24]
        cipher_encrypt = DES3.new(key, DES3.MODE_ECB)
        encrypted_text = cipher_encrypt.encrypt(
            pad(text.encode(ENCODING), DES3.block_size, style=PAD_STYLE)
        )
        return base64.b64encode(encrypted_text).decode(ENCODING)

    def decode_des3(self, text):
        byte_string = base64.b64decode(text)
        key = self.des_key[:24]
        cipher_encrypt = DES3.new(key, DES3.MODE_ECB)
        cipher_bytes = cipher_encrypt.decrypt(byte_string)
        cipher_str = str(cipher_bytes, encoding=ENCODING)
        cipher_clear = cipher_str[: cipher_str.rfind("}") + 1]
        return json.loads(cipher_clear, strict=False)

    @staticmethod
    def post(url, payload):
        """
        Call XHJ interface using the Requests library

        :param url: str, xhj full interface address
        :param payload: dict, returns a ciphertext object
            {
                "mchntNum": "mchntNum",
                "signature": "signature",
                "reqCipher": "reqCipher"
            }
        :return: dict
        """
        headers = {"Content-Type": "application/json", "charset": "UTF-8"}
        payload = json.dumps(payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def call(self, api_name, data):
        """
        Call the XHJ interface and decrypt the returned data
        :param api_name: str, example: sign/userverify
        :param data: dict, call plaintext objects required by different interfaces
        :return: dict
        """
        url = f"{self.base_url}/{api_name}"
        encrypt_data = dict(
            mchntNum=self.mchnt_num,
            signature=self.sign(data),
            reqCipher=self.encode_des3(json.dumps(data)),
        )
        res = self.post(url, encrypt_data)
        if res["respCode"] != "0000":
            return res
        decrypt_cipher = self.decode_des3(res.get("resCipher"))
        self.verify(decrypt_cipher, res["signature"])
        res["decryptResCipher"] = decrypt_cipher
        return res


class XHJ(DependencyProvider):
    def setup(self):
        self.xhj = XHJClient(nameko.config)

    def get_dependency(self, worker_ctx):
        return self.xhj
