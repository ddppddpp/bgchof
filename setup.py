try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()


setup(
    name="bgchof",
    description="(B)ul(g)arian (Ch)ristian (O)rthodox (F)asting",
    version="0.5.7",
    author="Ivailo Djilianov",
    url="https://www.github.com/ddppddpp/bgchof",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules=[
        "bgchof",
        "calculateEaster",
        "fastingIO",
        "fastingStatus",
        "generateCalendar",
    ],
    python_requires=">=3.9, <4",
)
