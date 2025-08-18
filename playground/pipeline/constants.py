IMPORT_HELPER = {
    "python": [
        "import math",
        "import re",
        "import sys",
        "import copy",
        "import datetime",
        "import itertools",
        "import collections",
        "import heapq",
        "import statistics",
        "import functools",
        "import hashlib",
        "import numpy",
        "import numpy as np",
        "import string",
        "from typing import *",
        "from collections import *",
    ],
    "go"    : [
        "math",
        "strings",
        "fmt",
        "strconv",
        "time",
        "bytes",
        "regexp",
        "sort",
        "math/rand",
        "crypto/md5",
        "encoding/hex",
    ],
    "cpp"   : [
        "#include<stdlib.h>",
        "#include<algorithm>",
        "#include<math.h>",
        "#include<stdio.h>",
        "#include<vector>",
        "#include<string>",
        "#include<climits>",
        "#include<cstring>",
        "#include<iostream>",
        "#include <numeric>",
        "#include <sstream>",
        "#include <stack>",
        "#include <cctype>",
        "#include <set>",
        "#include <unordered_set>",
        "#include <iomanip>",
    ],
}

LANG_PREFIX = {
    "cpp"          : "// language: C++",
    "java"         : "// language: Java",
    "js"           : "// language: JavaScript",
    "javascript"   : "// language: JavaScript",
    "go"           : "// language: Go",
    "python"       : "# language: Python",
}



HUMANEVAL_PROMPT_JAVA = """
Read the following function signature and docstring, and fully implement
the method described. Ensure your method signature is exactly the same as 
the one provided in the prompt. Ensure you include the `class Solution {}` 
classname. Your response should only contain the code, no explanations. 
Example outputs are provided below. 
```java
class Solution {
    public void testMethod1() {
        // method code
    }
}
```

```java
class Solution {
    public bool testMethod2(int a, int b) {
        // method code
    }

    public int helperMethod() {
        // helper method code.
    }
}
```\n
"""

HUMANEVAL_PROMPT = """
Read the following function signature and docstring, and fully implement
the function described. Include a function signature, that's exactly the 
same as the one provided in the prompt. Do NOT include any explanations. 
Also do NOT include the `main` function\n
"""



EXTRACTION_PROMPT_JAVA = """
Here is a section of code. Remove any import statements and block comments. 
Leave any indentation as it is (ie. don't remove leading whitespace for any line).\n
"""

EXTRACTION_PROMPT_GO = """
Here is a section of code. Remove any leading package names and comments. 
Leave any indentation as it is (ie. don't remove leading whitespace for any line).
Also leave any import statements, if present.\n
"""

EXTRACTION_PROMPT = """
Here is a section of code. Remove any leading package names, import statements, and comments. 
Leave any indentation as it is (ie. don't remove leading whitespace for any line).
If there is a `main` function present, remove it.\n
"""


