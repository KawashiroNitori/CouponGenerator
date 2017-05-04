import mimetypes
import shortuuid
import hashlib
from os import path
from os import rename

from coupon import app
from coupon import error
from coupon.util import validator
from coupon.util import options
from coupon.model import coupon
from coupon.model import telephone
from coupon.handler import base


FILE_MAX_LENGTH = 2 ** 25   # 32 MiB
ALLOWED_MIMETYPE_PREFIX = ['image/']


class ImageFileMixin(object):
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


@app.route('/coupon/create', 'coupon_create')
class CouponCreateHandler(base.Handler, ImageFileMixin):

    async def get(self):
        self.render('coupon_create.html')

    async def post(self):
        data = {}
        async for part in await self.request.multipart():
            if part.name != 'img':
                content = (await part.read()).decode()
                if content != '':
                    data[part.name] = content
            else:
                data['img'] = await self.handle_img_upload(part)

        if 'title' not in data:
            raise error.ValidationError('title')
        try:
            cid = coupon.add(**data)
        except TypeError:
            raise error.UnknownArgumentError()
        self.render('coupon_create_success.html', cid=cid)


@app.route('/coupon/{cid:\w{22}}', 'coupon_detail')
class CouponDetailHandler(base.Handler):

    @base.route_argument
    async def get(self, *, cid: str):
        coupon_row = coupon.get_by_uuid(cid)
        if not coupon_row:
            raise error.CouponNotFoundError(cid)
        coupon.inc_view(cid)
        img_url = coupon_row['img']
        self.render('coupon_detail.html', cid=cid, img_url=img_url,
                    page_title=coupon_row['title'],
                    receive_text=coupon_row['receive_text'], custom_style=coupon_row['custom_style'])

    @base.route_argument
    @base.post_argument
    async def post(self, *, cid: str, tel: str):
        validator.check_tel(tel)
        coupon_row = coupon.get_by_uuid(cid)
        if not coupon_row:
            raise error.CouponNotFoundError(cid)
        tel_id = telephone.add(coupon_row['id'], tel)
        coupon.inc_submit(cid)

        self.render('coupon_success.html')


@app.route('/coupon/{cid:\w{22}}/edit', 'coupon_edit')
class CouponEditHandler(base.Handler, ImageFileMixin):

    @base.route_argument
    async def get(self, *, cid: str):
        coupon_row = coupon.get_by_uuid(cid)
        if not coupon_row:
            raise error.CouponNotFoundError(cid)
        self.render('coupon_create.html', **coupon_row, edit=True)

    @base.route_argument
    async def post(self, cid: str):
        coupon_row = coupon.get_by_uuid(cid)
        if not coupon_row:
            raise error.CouponNotFoundError(cid)
        data = {}
        async for part in await self.request.multipart():
            if part.name != 'img':
                content = (await part.read()).decode()
                if content != '':
                    data[part.name] = content
            elif part.filename != '':
                data['img'] = await self.handle_img_upload(part)

        if 'title' not in data:
            raise error.ValidationError('title')
        try:
            cid = coupon.edit(cid, **data)
        except TypeError:
            raise error.UnknownArgumentError()
        self.redirect(self.reverse_url('coupon_detail', cid=cid))


@app.route('/coupon', 'coupon_main')
class CouponMainHandler(base.Handler):
    async def get(self):
        coupons = coupon.get_all()
        self.render('coupon_main.html', coupons=coupons)
