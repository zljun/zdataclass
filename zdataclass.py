from enum import IntEnum, IntFlag
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
TRACE_LEVEL_NONE = 0
TRACE_LEVEL_DEBUG = 1
TRACE_LEVEL_INFO = 2
TRACE_LEVEL_WARN = 3
TRACE_LEVEL_ERROR = 4

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
    
class uint5(base_int):
    W = 5/8
    ENDIAN = 'little'

class uint6(base_int):
    W = 6/8
    ENDIAN = 'little'

class uint7(base_int):
    W = 7/8
    ENDIAN = 'little'

class uint9(base_int):
    W = 9/8
    ENDIAN = 'little'

class uint10(base_int):
    W = 10/8
    ENDIAN = 'little'

class uint11(base_int):
    W = 11/8
    ENDIAN = 'little'

class uint12(base_int):
    W = 12/8
    ENDIAN = 'little'

class uint13(base_int):
    W = 13/8
    ENDIAN = 'little'

class uint14(base_int):
    W = 14/8
    ENDIAN = 'little'

class uint15(base_int):
    W = 15/8
    ENDIAN = 'little'
    
class IntEnum8(IntEnum):    
    def __len__(self):
        return 1
    def is_member(self, value):
        for x in self.__members__:
            if self.__members__[x] == value:
                return True
        return False

class IntEnum16(IntEnum):    
    def __len__(self):
        return 2
        
class IntFlag8(IntFlag):    
    def __len__(self):
        return 1

class IntFlag16(IntFlag):    
    def __len__(self):
        return 2

class IntFlag32(IntFlag):    
    def __len__(self):
        return 4

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
	
class type_len_data_t():
    def __len__(self): # including size field
        return self.real_size + self.offset

    def unpack(self, data, n, mask=None): 
        if len(data) <abs(n):
            logger_cotypes.warn('int_array len(data)={} <{}'.format(len(data), abs(n)))
            return self
        if n <0:
            self.size = int.from_bytes(data[0:abs(n)], self.ENDIAN)
            self.offset = abs(n)
        else:
            self.size = n * self.W
            self.offset = 0
        if mask == None:
            self.real_size = self.size
        else:
            self.real_size = self.size & mask
        self.n_items = int(self.real_size / self.W)
        self.array = list()
        W = self.W 
        if W*self.n_items + self.offset>len(data):
            logger_cotypes.warn('int_array not enough data: n_items={}'.format(self.n_items))
            return self 
        for i in range(self.n_items):
            idx = W*i + self.offset
            self.array.append(int.from_bytes(data[idx: idx+W], self.ENDIAN))
        return self

# sdp data element
# byte[0].bit[7:3] element type
class data_element_type(IntEnum):
    NULL = 0
    UINT = 1
    SINT = 2
    UUID = 3
    STRING = 4
    BOOL = 5
    DATA_ELEMENT_SEQ = 6
    DATA_ELEMENT_ALT = 7
    URL = 8

# sdp data element
# byte[0].bit[2:0] element size descriptor
class data_element_size_t(IntEnum):
    ONE = 0
    TWO = 1
    FOUR = 2
    EIGHT = 3
    SIXTEEN = 4
    IN_NEXT_U8 = 5
    IN_NEXT_U16 = 6
    IN_NEXT_U32 = 7  
    
class sdp_data_element_t():
    def __init__(self, element_type=None, element_size=None, element_data=None):
        self.element_type = element_type
        if element_size !=None:
            self.set_element_size(element_size)
        self.element_data = element_data

    def set_element_size(self, element_size):
        self.element_size = element_size
        if element_size == 1:
            self.element_size_desc = data_element_size_t.ONE
        elif element_size == 2:
            self.element_size_desc = data_element_size_t.TWO
        elif element_size == 4:
            self.element_size_desc = data_element_size_t.FOUR
        elif element_size == 8:
            self.element_size_desc = data_element_size_t.EIGHT
        elif element_size == 16:
            self.element_size_desc = data_element_size_t.SIXTEEN
        elif element_size <256:
            self.element_size_desc = data_element_size_t.IN_NEXT_U8
        elif element_size <65536:
            self.element_size_desc = data_element_size_t.IN_NEXT_U16
        else:
            self.element_size_desc = data_element_size_t.IN_NEXT_U32

    def to_bytes(self):
        if self.element_type == data_element_type.NULL:
            return (self.element_type<<5).to_bytes(1, 'big')
            
        if self.element_type == None or self.element_size == None or self.element_data == None:
            return b''
            
        data = (((self.element_type&0x1F)<<3) | (self.element_size_desc&0x07)).to_bytes(1, 'big')
        if self.element_size_desc == data_element_size_t.IN_NEXT_U8:
            data += self.element_size.to_bytes(1, 'big')
        elif self.element_size_desc == data_element_size_t.IN_NEXT_U16:
            data += self.element_size.to_bytes(2, 'big')  
        elif self.element_size_desc == data_element_size_t.IN_NEXT_U32:
            data += self.element_size.to_bytes(4, 'big')
        if self.element_type in [data_element_type.UINT, data_element_type.SINT, data_element_type.BOOL]:
            W = 1 <<self.element_size_desc
            data += self.element_data.to_bytes(W, 'big')
        elif self.element_type in [data_element_type.UUID, data_element_type.STRING]:
            data += bytes(self.element_data)
        elif self.element_type in [data_element_type.DATA_ELEMENT_SEQ, data_element_type.DATA_ELEMENT_ALT]:
            for ele in self.element_data:
                data += ele.to_bytes()
        else:
            logger_cotypes.error('Unknown element type {}'.format(self.element_type))
        
        return data

    def from_bytes(self, data):
        if len(data) == 0:
            self.element_type = data_element_type.NULL
            self.element_size_desc = 0
            self.element_size = 0
            self.element_data = b''
            return
        try:
            self.element_type = data_element_type(data[0] >>3)
        except:
            self.element_type = data[0] >>3
        self.element_size_desc = data_element_size_t(data[0] & 0x07)
        if self.element_size_desc <= data_element_size_t.SIXTEEN:
            self.element_size = 1 <<self.element_size_desc
            offset = 1
        elif self.element_size_desc == data_element_size_t.IN_NEXT_U8:
            self.element_size = data[1]
            offset = 2
        elif self.element_size_desc == data_element_size_t.IN_NEXT_U16:
            self.element_size = int.from_bytes(data[1:3], 'big')
            offset = 3
        elif self.element_size_desc == data_element_size_t.IN_NEXT_U32:
            self.element_size = int.from_bytes(data[1:5], 'big')
            offset = 5
            
        if self.element_type == data_element_type.NULL:
            self.element_data = None
        elif self.element_type == data_element_type.UINT:
            self.element_data = int.from_bytes(data[offset:offset+self.element_size], 'big')
        elif self.element_type == data_element_type.SINT:
            self.element_data = int.from_bytes(data[offset:offset+self.element_size], 'big', signed=True)
        elif self.element_type == data_element_type.UUID:
            self.element_data = data[offset:offset+self.element_size]
        elif self.element_type == data_element_type.DATA_ELEMENT_SEQ:
            count = self.element_size
            self.element_data = []
            while count >0:
                ele = sdp_data_element_t().from_bytes(data[offset:])
                offset += len(ele)
                count -= len(ele)
                self.element_data.append(ele)
        else:
            self.element_data = data[offset:offset+self.element_size]
        return self
                
    def __len__(self):
        if self.element_size_desc <= data_element_size_t.SIXTEEN:
            offset = 1
        elif self.element_size_desc == data_element_size_t.IN_NEXT_U8:
            offset = 2
        elif self.element_size_desc == data_element_size_t.IN_NEXT_U16:
            offset = 3
        elif self.element_size_desc == data_element_size_t.IN_NEXT_U32:
            offset = 5
        return self.element_size + offset
        
    def __repr__(self):
        format_str = 'data element {}: size={}'.format(repr(self.element_type), self.element_size)
        if True: #type(self.element_data) != list:
            format_str += ', data={}'.format(self.element_data)
            self.repr = format_str
            return format_str
        format_str += ', data:\r\n'
        for d in self.element_data:
            format_str += '\r\n    {}'.format(d)
        self.repr = format_str
        return self.repr        

@dataclass
class basedataclass:    
    def __post_init__(self):
        self.trace_level = TRACE_LEVEL_NONE
        # Deal with special fields from tail to head. A field is union and <length, value> type 
        for x in dataclasses.fields(self)[::-1]: 
            fieldname = getattr(x, 'name')
            # A length field is initialized with length of its data-field
            data_field = self.is_length_field(x)
            if data_field != None: 
                setattr(self, fieldname, len(getattr(self,data_field)))

            # A union field shall be bytearray and be packed with its following fields
            self.bit_offset = 0
            self.bitfields = []
            if self.is_union_field(x):
                found = False
                m = b''
                for y in dataclasses.fields(self):
                    if x == y:
                        found = True
                        continue
                    if found == True:
                        try:
                            fieldtype = getattr(y, 'type')
                            if fieldtype in base_int.__subclasses__() and fieldtype.W !=int(fieldtype.W):
                                fieldname1 = getattr(y, 'name')
                                value = getattr(self, fieldname1)
                                self.bit_offset += int(fieldtype.W * 8)
                                self.bitfields.append((int(fieldtype.W * 8), value))
                                if self.bit_offset & 7 == 0:
                                    m += self.pack_bitfields(self.bitfields)
                                    self.bit_offset = 0
                                    self.bitfields = []
                            else:
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
                 
        #raise Exception('Unknown length for field {}'.format(x))
        return 0

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
        offset = 0
        result = 0
        for x in bitfields:
            n_bits = x[0]
            value = x[1]
            result |= (value <<offset)
            offset += n_bits 
        return result.to_bytes(offset//8, 'little')

    def debug(self, s):
        if logger_zdataclass != None:
            logger_zdataclass.debug(s)
        elif self.trace_level >=TRACE_LEVEL_DEBUG:
            print(s)
            
    def info(self, s):
        if logger_zdataclass != None:
            logger_zdataclass.info(s)
        elif self.trace_level >=TRACE_LEVEL_INFO:
            print(s)
			
    def warn(self, s):
        if logger_zdataclass != None:
            logger_zdataclass.info(s)
        elif self.trace_level >=TRACE_LEVEL_INFO:
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
                self.bitfields.append((int(fieldtype.W * 8), value))
                if self.bit_offset & 7 == 0:
                    data += self.pack_bitfields(self.bitfields)
                    self.bit_offset = 0
                    self.bitfields = []
            else:
                data += self.pack_field(x)
        return data

    def unpack_bitfields(self, bitfields, data):
        offset = 0
        word = int.from_bytes(data[0:4], 'little')
        for x in bitfields:
            n_bits = x[0]
            fieldname = x[1]
            value = (word >>offset) & ((1<<n_bits) - 1)
            offset += n_bits
            setattr(self, fieldname, value)
        return offset // 8
  
    def unpack1(self, data):
        if len(data) < len(self):
            raise Exception('data length {} less than expected {}'.format(len(data), len(self)))

        self.info('unpack {}'.format(type(self)))
        offset = 0
        self.bit_offset = 0
        self.bitfields = []
        for x in dataclasses.fields(self): 
            default = getattr(x, 'default')
            metadata = getattr(x, 'metadata')
            fieldname = getattr(x, 'name')
            t = getattr(x, 'type')
            L = self.get_field_len(x, data)

            if t in base_int.__subclasses__() and t.W !=int(t.W):
                self.bit_offset += int(t.W * 8)
                self.bitfields.append((int(t.W * 8), fieldname, default))
                if self.bit_offset & 7 == 0:
                    L = self.unpack_bitfields(self.bitfields, data[offset:] )
                    for bitfield in self.bitfields:
                        value = getattr(self, bitfield[1])
                        default = bitfield[2]
                        if default != None and default != value and type(default) !=dataclasses._MISSING_TYPE:
                            return None
        
                    self.bit_offset = 0
                    self.bitfields = []
            elif t == str:
                value = str(data[offset:offset+L], 'utf-8')
            elif t in [bytearray, bytes]:
                value = data[offset:offset+L]
            else:
                try:
                    if t != sdp_data_element_t:
                        value = t.from_bytes(data[offset:offset+L])
                    else:
                        value = sdp_data_element_t().from_bytes(data[offset:])
                        L = len(value)
                except Exception as e:
                    print(e)
                    raise e
          
            if self.is_union_field(x) == False and int(L) == L:
                offset += L

            if t in base_int.__subclasses__() and t.W !=int(t.W):                
                continue

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

@dataclass
class s_with_bitfield(basedataclass):
    data: bytearray = dataclasses.field(default_factory=bytearray, metadata={LENGTH_FIELD:4, UNION_FIELD:True})
    head: uint8 = None
    handle:  uint12 = None
    pb_flag: uint2 = None
    bc_flag: uint2 = None
    tail: uint8 = None
   
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

def test_bitfield():
    d = s_with_bitfield(head=0, pb_flag=1, bc_flag=2, handle=0x20, tail=255)
    print('{}, len={}'.format(d, len(d)))
    data = d.pack()
    print(hexlify(data))

    d2 = s_with_bitfield().unpack(data)
    print('{}, len={}'.format(d2, len(d2)))

    if d2 == d:
        print('test_bitfield pass\r\n')
    else:
        print('test_bitfield fail\r\n')

if __name__ == '__main__':
    '''test_length_field()
    test_union_field()   
    test_int_array()'''
    test_bitfield()
    
    
