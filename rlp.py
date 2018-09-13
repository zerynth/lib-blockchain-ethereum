"""

.. module:: rlp

***
RLP
***

This module implements the RLP encoding scheme for the Ethereum protocol.


    """

def _to_bytes(x):
    if type(x) == PSMALLINT or type(x)==PINTEGER:
        if x==0:
            return b''
        # big endian, no leading 0
        ret = bytearray(4)
        ret[0] = (x>>24)&0xff
        ret[1] = (x>>16)&0xff
        ret[2] = (x>>8)&0xff
        ret[3] = (x)&0xff
        j = -1
        for i in range(0,3):
            if ret[i]==0:
                j=i
            else:
                break
        return ret[j+1:]
    if type(x) in (PSTRING,PBYTES,PBYTEARRAY):
        return x


def encode(obj):
    """
.. function:: encode(obj)

    :param obj: the object to encode

	Return the RLP representation of *obj*.
	Only lists, tuples, strings, bytes/bytearrays and integers are allowed as types for *obj*.

    """
    if type(obj) in (PLIST,PTUPLE):
        b = bytearray()
        for item in obj:
            ii = encode(item)
            b.extend(ii)
        return encode_length(len(b),192)+b
    else:
        b = _to_bytes(obj)
        if len(b)==1 and b[0]<128:
            return b
        else:
            return encode_length(len(b),128)+b


def encode_length(l,ofs):
    b = bytearray(1)
    if l<56:
        b[0] = l+ofs
        return b
    else:
        bl = to_binary(l)
        b[0] = len(bl)+ofs+55
        return b+bl

def to_binary(x):
    m = bytearray(1)
    m[0]=x%256
    return '' if x == 0 else to_binary(x // 256) + m


