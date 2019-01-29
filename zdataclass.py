from enum import IntEnum, IntFlag
from dataclasses import dataclass
import dataclasses
from binascii import hexlify
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger_zdataclass = logging.getLogger(__name__)

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
        
    def __len__(self):
        if self.W == None:
            raise Exception('object of type ({}) has no length'.format(type(self)))
        return self.W

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
    
class BaseIntEnum(IntEnum):
    def is_valid(self, value):
        for x in self.__members__:
            if self.__members__[x] == value:
                return True
        return False

class IntEnum8(BaseIntEnum):    
    def __len__(self):
        return 1
    
class IntEnum16(BaseIntEnum):    
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
        
    def __len__(self): # including size field
        return len(self.array) * self.W

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
  def __post_init__(self):
    # Deal with special fields from tail to head. A field is union and <length, value> type 
    for x in dataclasses.fields(self)[::-1]: 
      fieldname = getattr(x, 'name')
      data_field = self.is_length_field(x)
      if data_field != None: 
        setattr(self, fieldname, len(getattr(self,data_field)))
        
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
                except:
                  pass
        if len(m):
          setattr(self, fieldname, m)

      # make sure attribyte value matches its type
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

    t = getattr(x, 'type')
    if (t in int_array.__subclasses__()) and (length !=None):
      length *= t.W
    return length
    
  def get_field_len(self, x, data=None):
    t = getattr(x, 'type')
    # length determined by field type, shall be first check
    if t not in ([bytearray, bytes, str, int] + int_array.__subclasses__()): 
      try:
        m = len(t())
      except Exception as e:
        logger_zdataclass.error('Type {} doesnt hint its length.{}'.format(t,e))
        return 0
      return m

    # field length determined by metadata
    m = self.get_field_len_from_metadata(x)
    if m !=None:
      return m

    # length determined by field (default) value
    if (t in [bytearray, bytes, str]):
      fieldname = getattr(x, 'name')
      value = getattr(self, fieldname)
      if value != None:
        return len(value)
      default = getattr(x, 'default')
      if default !=None and type(default) !=dataclasses._MISSING_TYPE:
        return len(default)
          
    # length of string with terminator     
    if t == str and data !=None:
      terminator_found = False
      m = 0
      for x in data[offset:]:
        if x == 0x00:
          terminator_found = True
          break
        m +=1
      if terminator_found:
        return m

    # length determined by another field whose name specified by metadata
    metadata = getattr(x, 'metadata')
    try:
        lf = metadata[LENGTH_FIELD]
        length = getattr(self, lf)
    except:
        lf = None
        length = None    
    if (lf !=None) and (length !=None):
        return length  
             
    #logger_zdataclass.error('Unknown length for field {}'.format(x))
    return 0

  def __len__(self):
    n = 0
    for x in dataclasses.fields(self): 
      # UNION fields shall not contribute length for multiple times
      if self.is_union_field(x):
        last_field = dataclasses.fields(self)[-1]
        if x !=last_field: # not last field
          continue
      n += self.get_field_len(x)
    return n
    
  def pack_field(self, x):
    fieldname = getattr(x, 'name')
    if self.is_union_field(x):
      if x !=dataclasses.fields(self)[-1]:
        return b''
      else:
        return getattr(self, fieldname)
        
    data = b''  
    t = getattr(x, 'type')
    L = self.get_field_len(x)     
    value = getattr(self, fieldname)
    logger_zdataclass.debug('pack field {}, L={}, value={}, type={}'.format(fieldname, L, value, t))
    
    if t in [uint8, uint16, uint24, uint32, uint64, int8, int16, int32]:
      data += value.to_bytes(L, 'little')
    elif t in [uint16_be, uint32_be, uint64_be]:
      data += value.to_bytes(L, 'big')       
    elif t in [bytearray, str]:
      data += bytes(value)
    elif t in int_array.__subclasses__():
      for y in value.array:
        data += y.to_bytes(t.W, t.ENDIAN)
    elif t == sdp_data_element_t:
        data += value.to_bytes()
    else:
      logger_zdataclass('dont known how to pack.')
    return data
        
  def pack(self):
    data = b''
    logger_zdataclass.info('pack {}'.format(type(self)))
    for x in dataclasses.fields(self): 
      data += self.pack_field(x)
    return data
  
  def unpack1(self, data):
    if len(data) < len(self):
      logger_zdataclass.error('data length {} less than expected {}'.format(len(data), len(self)))
      return None

    logger_zdataclass.info('unpack {}'.format(type(self)))
    offset = 0  
    for x in dataclasses.fields(self): 
      default = getattr(x, 'default')
      metadata = getattr(x, 'metadata')
      fieldname = getattr(x, 'name')
      t = getattr(x, 'type')
      L = self.get_field_len(x, data)

      if t in [uint8, uint16, uint24, uint32, uint64, int8, int16, int32]:
        value = int.from_bytes(data[offset:offset+L], 'little')
      elif t in [uint16_be, uint32_be, uint64_be]:
        value = int.from_bytes(data[offset:offset+L], 'big')        
      elif t == str:
        value = str(data[offset:offset+L], 'utf-8')
      elif t in [bytearray]:
        value = data[offset:offset+L]
      elif t in int_array.__subclasses__():
        value = getattr(self,fieldname)        
        n_items = L // t.W  
        for i in range(n_items):
          idx = t.W*i + offset
          value.array.append(int.from_bytes(data[idx: idx+t.W], t.ENDIAN))
      elif t == sdp_data_element_t:
          value = sdp_data_element_t().unpack(data[offset:])
          L = len(value)
      else:
        logger_zdataclass.warn('type {} not parserable'.format(t))
        continue
      logger_zdataclass.debug('fieldname={}, L={}, value={}'.format(fieldname, L, value))

      if self.is_union_field(x) == False:
        offset += L

      # field with default value shall be same as unpacked value
      if default != None and default != value and type(default) !=dataclasses._MISSING_TYPE:
        logger_zdataclass.debug('unpack fail: value({}) !=default({})'.format(value, default))
        return None

      if type(value) != t:
	      try:
	          value = t(value)
	      except:
	          pass
      setattr(self, fieldname, value)  # set field value and type convert
    logger_zdataclass.info('unpack succeed {}'.format(type(self)))
    return self
    
  def unpack(self, data):
    ''''ret = self.unpack1(data, endian, dbg_en)
    return ret'''
    try:
        ret = self.unpack1(data)
        #self.__post_init__() # do it to initialize special fields (union fields)
        return ret
    except Exception as e:
        print(e)
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
class s_with_auto_field(basedataclass):
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
    array16: uint16_array = dataclasses.field(default_factory=uint16_array, metadata={LENGTH_FIELD:2})
    array32: uint32_array = dataclasses.field(default_factory=uint32_array, metadata={LENGTH_FIELD:1})
   
def test_auto_field():
    d = s_with_auto_field(data=b'\xAA\x55')
    print('{}, len={}'.format(d, len(d)))  
    print(d.pack())
    
    d = s_with_auto_field().unpack(b'\x02\xAA\x55')
    print('{}, len={}'.format(d, len(d)))  
    
def test_union_field():
    d = s_with_union_field(cid=0x0040)
    print('{}, len={}'.format(d, len(d)))
    
    
    data = d.pack()
    d = s_with_union_field().unpack(data)
    print('{}, len={}'.format(d, len(d)))     


def test_int_array():
    d = s_with_int_array(array8=[0x01, 0x02],
                         array16=[0x0001, 0x0002],
                         array32=[0x00000001])
    print('{}, len={}'.format(d, len(d)))  
    
    data = d.pack()
    d = s_with_int_array()
    d.unpack(data)
    print('{}, len={}'.format(d, len(d)))   

def test_sdp_data_element():   
    ret = sdp_data_element_t(data_element_type.DATA_ELEMENT_SEQ)
    element_list = []
    size = 0
    uuid_list = [b'\x18\x00']
    for uuid in uuid_list:
        element = sdp_data_element_t(data_element_type.UUID, len(uuid), uuid)
        element_list.append(element)
        size += len(element)
    ret.set_element_size(size)
    ret.element_data = element_list

    data = ret.to_bytes()
    print(hexlify(data))

    ret = sdp_data_element_t().unpack(data)
    print(ret)

if __name__ == '__main__':
    #test_auto_field()
    #test_union_field()   
    #test_int_array()
    test_sdp_data_element()
    
    
