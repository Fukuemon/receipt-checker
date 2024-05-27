from setuptools import setup, Extension

from Cython.Build import cythonize
import Cython.Compiler.Options
Cython.Compiler.Options.docstrings = False

ext_modules = cythonize(
    [
        #module1
        Extension("libs.mymodule01", ["libs/function.py"]),

        #module2
        Extension("libs.mymodule02", ["libs/const_data.py"]),

    ], compiler_directives=dict(
            language_level="3",
            always_allow_keywords=True
        )
)

setup(
    name="receipt_check",
    version='1.0.0',
    ext_modules=ext_modules,
    author="hoge",
    author_email="example@gmail.com",
)