import mimetypes
import shortuuid
import hashlib
from os import path
from os import rename

from coupon import app
from coupon import error
from coupon.util import options
from coupon.model import coupon
from coupon.model import telephone
from coupon.handler import base


FILE_MAX_LENGTH = 2 ** 25   # 32 MiB
ALLOWED_MIMETYPE_PREFIX = ['image/']


@app.route('/coupon/create', 'coupon_create')
class CouponCreateHandler(base.Handler):

    async def handle_img_upload(self, part):
        img_filename = part.filename
        content_type, img_extension = self.get_content_type(img_filename)
        tmp_filename = shortuuid.uuid() + img_extension
        md5 = hashlib.md5()
        tmp_path = path.join(options.options.img_static_path, tmp_filename)
        with open(tmp_path, 'wb') as file:
            while True:
                chunk = await part.read_chunk()
                if not chunk:
                    break
                file.write(chunk)
                md5.update(chunk)
        img_filename = md5.hexdigest() + img_extension
        rename(tmp_path, path.join(options.options.img_static_path, img_filename))
        return img_filename

    @staticmethod
    def get_content_type(filename):
        content_type = mimetypes.guess_type(filename)[0]
        if not content_type or not any(content_type.startswith(allowed_type)
                                       for allowed_type in ALLOWED_MIMETYPE_PREFIX):
            raise error.FileTypeNotAllowedError(filename, content_type)
        return content_type, mimetypes.guess_extension(content_type)

    async def get(self):
        self.render('coupon_create.html')

    async def post(self):
        data = {}
        async for part in await self.request.multipart():
            if part.name != 'img':
                data[part.name] = (await part.read()).decode()
            else:
                data['img'] = await self.handle_img_upload(part)

        name = data['name']
        img_filename = data['img']
        cid = await coupon.add(name, img_filename)
        self.redirect(self.reverse_url('coupon_detail', cid=cid))

