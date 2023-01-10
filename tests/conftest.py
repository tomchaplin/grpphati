from hypothesis import settings

settings.register_profile("long", max_examples=1000)
settings.register_profile("overnight", max_examples=200000)
