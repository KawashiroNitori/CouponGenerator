from distutils.core import setup

setup(
    name='CouponGenerator',
    version='0.1',
    packages=['coupon',
              ],
    url='',
    license='',
    author='Nitori',
    author_email='nitori@ikazuchi.cn',
    description='Coupon Page Generator',
    install_requires=open('requirements.txt').readlines(),
)
