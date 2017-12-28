from django.test import TestCase

# Create your tests here.
import json

v={"k":"吧唧","age":18}
print(json.dumps(v))
print(json.dumps(v,ensure_ascii=False))