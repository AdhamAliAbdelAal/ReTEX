def test ():
    return  {
    "s0":{
        "name":"test",
        "type":"test",
        "value":"test",
    }
}

def test2 ():
    return  {
    "s2":{
        "name":"test2",
        "type":"test2",
        "value":"test2",
    }
}

last = {
    "start": "S0",
    **test(),
    **test2()
}

print(last)