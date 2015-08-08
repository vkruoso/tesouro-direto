tesouro-direto
==============

|pypi| |travis| |license|

Set of tools to allow automated information recovery from your
"Tesouro Direto" account.

.. contents::
   :local:

.. |pypi| image:: https://img.shields.io/pypi/v/tesouro-direto.svg?style=flat-square
    :target: https://pypi.python.org/pypi/tesouro-direto

.. |travis| image:: https://img.shields.io/travis/vkruoso/tesouro-direto.svg?style=flat-square
    :target: https://travis-ci.org/vkruoso/tesouro-direto
    :alt: Build Status

.. |license| image:: https://img.shields.io/dub/l/vibe-d.svg?style=flat-square


Installation
------------

To install the tool the easiest way is to use pip::

    pip install tesouro-direto


Available tools
---------------

The main goal of this module is to generate an email that keeps you updated
regarding your titles. It also aims to provide some numbers that you can
use to have a better idea of how your money is working for you.


Email Report
++++++++++++

The email report allows you to have very in depth view of your titles. It
lists them based on the brokerage and them on the titles you have.

Besides that it will provide the following information:

  * Summaries of all your titles;
  * Calculations about your title current situation.

Here is a sample email screenshot:
(todo)


Configuring Crontab
^^^^^^^^^^^^^^^^^^^

You can configure `crontab` to call the program above. This way you can have
a automated email at the time and periodicity that you like.


Work Days Calculation
+++++++++++++++++++++

There is a simple module that can calculate the amount of work days between
two dates based on Brazilian national holidays. You can use it in your
program if you like by importing the module.
