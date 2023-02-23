from setuptools import setup, find_packages

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(name='my-jobs',
      version="0.0.1",
      description="Tracking and analysis of job application data 2023",
      license="MIT",
      author="Emily Cardwell",
      author_email="emily@emilycardwell.com",
      install_requires=requirements,
      packages=find_packages(),)
