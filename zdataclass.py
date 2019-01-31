from dataclasses import dataclass
import dataclasses
from binascii import hexlify
import logging
import logging.config

try:
    logging.config.fileConfig('logging.conf')
    logger_zdataclass = logging.getLogger(__name__)
except:
    logger_zdataclass = None

# see example s_with_auto_field
LENGTH_FIELD = 'length' 
DATA_FIELD = 'data'
LENGTH_OFFSET = 'offset'

# A field with this decorator share same space with its following fields 
UNION_FIELD = 'union'

class base_int(int):
    W = None
    ENDIAN = None
    
    def to_bytes(self):
        if self.W == None or self.ENDIAN == None:
            raise Exception('object of type ({}) has no to_bytes()'.format(type(self)))
        return int(self).to_bytes(self.W, self.ENDIAN)

    @classmethod
    def from_bytes(cls, data):
        if cls.ENDIAN == None:
            raise Exception('endian is unknown')
        if cls.W != None:
            data = data[0:cls.W]
        return int.from_bytes(data, cls.ENDIAN)

    @classmethod    
    def __len__(cls):
        if cls.W == None:
            raise Exception('object of type ({}) has no length'.format(cls))
        return cls.W

    def __repr__(self):
        if self.W == 1:
            self.repr = '0x{:02x}({})'.format(self, self)
        elif self.W == 2:
            self.repr = '0x{:04x}({})'.format(self, self)
        elif self.W == 3:
            self.repr = '0x{:06x}({})'.format(self, self)
        elif self.W == 4:
            self.repr = '0x{:08x}({})'.format(self, self)
        elif self.W == 8:
            self.repr = '0x{:016x}({})'.format(self, self)
        elif self.W == 16:
            self.repr = '0x{:032x}({})'.format(self, self)
        else:
            self.repr = '{}'.format(self)
        return self.repr

class int8(base_int): 
    W = 1
    ENDIAN = 'little'

class int16(base_int):    
    W = 2
    ENDIAN = 'little'

class int24(base_int):    
    W = 3
    ENDIAN = 'little'    

class int32(base_int):    
    W = 4
    ENDIAN = 'little'

class uint8(base_int):    
    W = 1
    ENDIAN = 'little'

class uint16(base_int):    
    W = 2
    ENDIAN = 'little'

class uint24(base_int):    
    W = 3
    ENDIAN = 'little'

class uint32(base_int):    
    W = 4
    ENDIAN = 'little'

class uint64(base_int):    
    W = 8
    ENDIAN = 'little'

class uint128(base_int):    
    W = 16
    ENDIAN = 'little'

class uint16_be(base_int):
    W = 2
    ENDIAN = 'big'
    
class uint32_be(base_int):
    W = 4
    ENDIAN = 'big'
   
class uint64_be(base_int):
    W = 8
    ENDIAN = 'big'

class uint128_be(base_int):    
    W = 16
    ENDIAN = 'big'

class uint1(base_int):
    W = 1/8
    ENDIAN = 'little'

class uint2(base_int):
    W = 2/8
    ENDIAN = 'little'

class uint3(base_int):
    W = 3/8
    ENDIAN = 'little'

class uint4(base_int):
    W = 4/8
    ENDIAN = 'little'

class int_array():
    W = None
    ENDIAN = None
    def __init__(self, array=None):
        if type(array) == list:
            self.array = array
        elif type(array) in [bytes, bytearray]:
            self.array = list(array)
        else:
            self.array = list()

    def to_bytes(self):
        if self.W == None or self.ENDIAN == None:
            raise Exception('object of type ({}) has no to_bytes()'.format(type(self)))
        result = b''
        for x in self.array:
            result += int(x).to_bytes(self.W, self.ENDIAN)
        return result

    @classmethod
    def from_bytes(cls, data):
        if cls.W == None or cls.ENDIAN == None:
            raise Exception('word width or endian is unknown')
        offset = 0
        array = []
        while offset <len(data):
            array.append(int.from_bytes(data[offset:offset+cls.W], cls.ENDIAN))
            offset += cls.W
        return array
        
    def __len__(self): # including size field
        if self.W == None:
            raise Exception('object of type ({}) has no len()'.format(type(self)))
        return len(self.array) * self.W

    def __eq__(self, other):
        if type(other) !=type(self):
            return False
        if self.array == other.array:
            return True
        else:
            return False

    def __repr__(self):
        if self.W == None:
            return repr(self)
        
        i = 0
        n_items = len(self.array)
        self.repr = 'array[{}]:'.format(n_items)
        while i<n_items:
            if i%(32/self.W) == 0: # each line 32 bytes
                self.repr += '\r\n'
            if self.W == 1:
                self.repr += '{:02x} '.format(self.array[i])
            elif self.W == 2:
                self.repr += '{:04x} '.format(self.array[i])    
            elif self.W == 4:    
                self.repr += '{:08x} '.format(self.array[i])
            else:
                self.repr += '{}'.format(self.array[i])
            i += 1
        self.repr += '\r\n'
        return self.repr
    
class uint8_array(int_array):   
    W=1
    ENDIAN = 'little'

class uint16_array(int_array):   
    W=2
    ENDIAN = 'little'
    
class uint32_array(int_array):   
    W=4
    ENDIAN = 'little'

@dataclass
class basedataclass:
    TRACE_LEVEL_NONE = 0
    TRACE_LEVEL_DEBUG = 1
    TRACE_LEVEL_INFO = 2
    TRACE_LEVEL_WARN = 3
    TRACE_LEVEL_ERROR = 4
    def __post_init__(self):
        self.trace_level = self.TRACE_LEVEL_NONE
        # Deal with special fields from tail to head. A field is union and <length, value> type 
        for x in dataclasses.fields(self)[::-1]: 
            fieldname = getattr(x, 'name')
            # A length field is initialized with length of its data-field
            data_field = self.is_length_field(x)
            if data_field != None: 
                setattr(self, fieldname, len(getattr(self,data_field)))

            # A union field shall be bytearray and be packed with its following fields
            if self.is_union_field(x):
                found = False
                m = b''
                for y in dataclasses.fields(self):
                    if x == y:
                        found = True
                        continue
                    if found == True:
                        try:
                            m += self.pack_field(y)
                        except Exception as e:
                            pass
                if len(m):
                    setattr(self, fieldname, m)

        # make sure attribute value matches its type
        for x in dataclasses.fields(self):
            fieldname = getattr(x, 'name')
            t = getattr(x, 'type')
            value = getattr(self, fieldname)
            if value != None and type(value) !=t:
                try: 
                    value = t(value)
                    setattr(self, fieldname, value)
                except:
                    pass
        
    def is_union_field(self, x):
        metadata = getattr(x, 'metadata')
        try:
            is_union = metadata[UNION_FIELD]
        except:
            is_union = False
        return is_union

    def is_length_field(self, x):
        metadata = getattr(x, 'metadata')
        try:
            field_name = metadata[DATA_FIELD]
        except:
            field_name = None
        return field_name

    def is_data_field(self, x):
        metadata = getattr(x, 'metadata')
        try:
            field_name = metadata[LENGTH_FIELD]
        except:
            field_name = None
        return field_name  

    def get_field_len_from_metadata(self, x):
        metadata = getattr(x, 'metadata')
        try:
            lf = metadata[LENGTH_FIELD]
            if type(lf) == str:
                length = getattr(self, lf)
            elif type(lf) == int:
                length = lf
            else:
                length = None
        except:
            length = None

        try:
            lf = metadata[LENGTH_OFFSET]
            if type(lf) == str:
                offset = getattr(self, lf)
            elif type(lf) == int:
                offset = lf
            else:
                offset = 0
        except:
            offset = 0
            
        if length != None:
          length += offset

        return length
    
    def get_field_len(self, x, data=None):
        t = getattr(x, 'type')
        # length determined by field type, shall be first check
        try:
            m = t.__len__()
        except Exception as e:
            m = None
        if m !=None:
            return m

        # field length determined by metadata
        m = self.get_field_len_from_metadata(x)
        if m !=None:
            return m

        # length determined by field (default) value
        fieldname = getattr(x, 'name')
        value = getattr(self, fieldname)
        try:
            m = len(value)
        except:
            m = None
        if m != None:
            return m
        
        default = getattr(x, 'default')
        try:
            m = len(default)
        except:
            m = None
        if m != None:
            return m  
                 
        raise Exception('Unknown length for field {}'.format(x))

    def __len__(self):
        n = 0
        for x in dataclasses.fields(self): 
            # if a union field is not the last field, it is replaced with its following fields   
            if self.is_union_field(x):
                last_field = dataclasses.fields(self)[-1]
                if x !=last_field: # not last field
                    continue
            n += self.get_field_len(x)
        if int(n) != n:
            self.warn('length {} is not integer'.format(n))
        return int(n)
    
    def pack_field(self, x):
        # if a union field is not the last field, it is replaced with its following fields      
        fieldname = getattr(x, 'name')
        if self.is_union_field(x):
            if x !=dataclasses.fields(self)[-1]:
                return b''
            else:
                value = getattr(self, fieldname)
                if type(value) not in [bytes, bytearray]:
                    self.warn('union field shall be of type bytes or bytearray')
                    return b''
                return value 
            
        data = b''  
        t = getattr(x, 'type')
        L = self.get_field_len(x)     
        value = getattr(self, fieldname)
        self.debug('pack field {}, L={}, value={}, type={}'.format(fieldname, L, value, t))

        if t in [bytearray, str]:
            data += bytes(value)
        else:
            if type(value) !=t:
                try:
                    value = t(value)
                except:
                    pass
            try:
                data += value.to_bytes()
            except Exception as e:
                raise e
        return data

    def pack_bitfields(self, bitfields):
        return b''

    def debug(self, s):
        if logger_zdataclass != None:
            logger_zdataclass.debug(s)
        elif self.trace_level >=self.TRACE_LEVEL_DEBUG:
            print(s)
            
    def info(self, s):
        if logger_zdataclass != None:
            logger_zdataclass.info(s)
        elif self.trace_level >=self.TRACE_LEVEL_INFO:
            print(s)
              
    def pack(self):
        self.bit_offset = 0
        self.bitfields = []
        data = b''
        self.info('pack {}'.format(type(self)))
        for x in dataclasses.fields(self):
            fieldtype = getattr(x, 'type')
            if fieldtype in base_int.__subclasses__() and fieldtype.W !=int(fieldtype.W):
                fieldname = getattr(x, 'name')
                value = getattr(self, fieldname)
                self.bit_offset += int(fieldtype.W * 8)
                self.bitfields.append((fieldtype.w, value))
                if self.bit_offset & 7 == 0:
                    data += self.pack_bitfields(self.bitfields)
                    self.bit_offset = 0
                    self.bitfields = []
            else:
                data += self.pack_field(x)
        return data
  
    def unpack1(self, data):
        if len(data) < len(self):
            raise Exception('data length {} less than expected {}'.format(len(data), len(self)))

        self.info('unpack {}'.format(type(self)))
        offset = 0  
        for x in dataclasses.fields(self): 
            default = getattr(x, 'default')
            metadata = getattr(x, 'metadata')
            fieldname = getattr(x, 'name')
            t = getattr(x, 'type')
            L = self.get_field_len(x, data)

            if t == str:
                value = str(data[offset:offset+L], 'utf-8')
            elif t in [bytearray, bytes]:
                value = data[offset:offset+L]
            else:
                try:
                    value = t.from_bytes(data[offset:offset+L])
                except Exception as e:
                    print(e)
                    raise e
          
            if self.is_union_field(x) == False:
                offset += L

            # field with default value shall be same as unpacked value
            if default != None and default != value and type(default) !=dataclasses._MISSING_TYPE:
                return None

            # type convert
            if type(value) != t:
                try:
                    value = t(value)
                except:
                    pass
            setattr(self, fieldname, value)  # set field value
        self.info('unpack succeed {}'.format(type(self)))
        return self
    
    def unpack(self, data):
        ''''ret = self.unpack1(data, endian, dbg_en)
        return ret'''
        try:
            ret = self.unpack1(data)
            return ret
        except Exception as e:
            return None

    def match(self, data, dbg_en=False):
        if self.unpack(data) == None:
            return False
        else:
            return True
          
    def almost_equal(self, other):
        if other.__class__ != self.__class__:
            return False
              
        for x in dataclasses.fields(self):   
            if self.is_union_field(x) or self.is_length_field(x) or self.is_data_field(x):
                continue
            fieldname = getattr(x, 'name')
            a = getattr(self, fieldname)
            b = getattr(other, fieldname)
            if a==None or b==None or a==b:
                continue
            else:
                return False
        return True

#------------------------ unit test -------------------------------- 
@dataclass
class s_with_length_field(basedataclass):
    length: uint8=dataclasses.field(default=None, metadata={DATA_FIELD:'data'})
    data: bytearray = dataclasses.field(default_factory=bytearray, metadata={LENGTH_FIELD:'length', UNION_FIELD:True})

@dataclass
class s_with_union_field(basedataclass):
    hci_length: uint16=dataclasses.field(default=None, metadata={DATA_FIELD:'hci_data'})
    hci_data: bytearray=dataclasses.field(default_factory=bytearray, metadata={UNION_FIELD:True, LENGTH_FIELD:'hci_length'})
    l2c_length: uint16 =dataclasses.field(default=None, metadata={DATA_FIELD:'l2c_data'})
    cid: uint16 = None
    l2c_data: bytearray=dataclasses.field(default_factory=bytearray, metadata={UNION_FIELD:True, LENGTH_FIELD:'l2c_length'})    

@dataclass
class s_with_int_array(basedataclass):
    array8: uint8_array = dataclasses.field(default_factory=uint8_array, metadata={LENGTH_FIELD:2})
    array16: uint16_array = dataclasses.field(default_factory=uint16_array, metadata={LENGTH_FIELD:2*2})
    array32: uint32_array = dataclasses.field(default_factory=uint32_array, metadata={LENGTH_FIELD:1*4})
   
def test_length_field():
    d = s_with_length_field(data=b'\x01\x02')
    print('{}, len={}'.format(d, len(d)))  
    print(hexlify(d.pack()))
    
    d2 = s_with_length_field().unpack(d.pack())
    print('{}, len={}'.format(d2, len(d2)))

    if d2 == d:
        print('test_length_field pass\r\n')
    else:
        print('test_length_field fail\r\n')
    
def test_union_field():
    d = s_with_union_field(cid=0x0040, l2c_data=b'\x01')
    print('{}, len={}'.format(d, len(d)))
    data = d.pack()
    print(hexlify(data))
    
    d2 = s_with_union_field().unpack(data)
    print('{}, len={}'.format(d2, len(d2)))

    if d2 == d:
        print('test_union_field pass\r\n')
    else:
        print('test_union_field fail\r\n')


def test_int_array():
    d = s_with_int_array(array8=[0x01, 0x02],
                         array16=[0x0001, 0x0002],
                         array32=[0x00000001])
    print('{}, len={}'.format(d, len(d)))  
    
    data = d.pack()
    print(hexlify(data))
          
    d2 = s_with_int_array().unpack(data)
    print('{}, len={}'.format(d2, len(d2)))

    if d2 == d:
        print('test_int_array pass\r\n')
    else:
        print('test_int_array fail\r\n')

if __name__ == '__main__':
    test_length_field()
    test_union_field()   
    test_int_array()
    
    
