# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: struct.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import constant_pb2 as constant__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='struct.proto',
  package='island',
  syntax='proto2',
  serialized_pb=_b('\n\x0cstruct.proto\x12\x06island\x1a\x0e\x63onstant.proto\"2\n\nGameServer\x12\n\n\x02id\x18\x01 \x02(\x05\x12\n\n\x02ip\x18\x02 \x02(\t\x12\x0c\n\x04port\x18\x03 \x02(\x05\"\x88\x01\n\x06Player\x12\x0b\n\x03uid\x18\x01 \x02(\x05\x12\x0c\n\x04team\x18\x02 \x02(\x05\x12\r\n\x05\x63olor\x18\x03 \x02(\x05\x12\x0c\n\x04name\x18\x04 \x02(\t\x12$\n\tcommander\x18\x05 \x02(\x0b\x32\x11.island.Commander\x12\x11\n\tis_online\x18\x07 \x02(\x08\x12\r\n\x05power\x18\x08 \x02(\x05\"L\n\tCommander\x12\x0b\n\x03\x63id\x18\x01 \x02(\x05\x12\x0c\n\x04name\x18\x02 \x02(\t\x12$\n\nproperties\x18\x03 \x03(\x0b\x32\x10.island.Property\"=\n\tGameState\x12\x0f\n\x07game_id\x18\x01 \x02(\x05\x12\x1f\n\x07players\x18\x02 \x03(\x0b\x32\x0e.island.Player\"\x9d\x01\n\x06Island\x12\n\n\x02id\x18\x01 \x02(\x05\x12\'\n\x0bisland_type\x18\x02 \x02(\x0e\x32\x12.island.IslandType\x12\t\n\x01x\x18\x03 \x02(\x02\x12\t\n\x01y\x18\x04 \x02(\x02\x12\x12\n\nmax_troops\x18\x05 \x02(\x05\x12\x0e\n\x06radius\x18\x06 \x02(\x02\x12\x12\n\ngun_radius\x18\x07 \x01(\x02\x12\x10\n\x08gun_life\x18\x08 \x01(\x05\"\xad\x02\n\x05\x46orce\x12\n\n\x02id\x18\x01 \x02(\x05\x12%\n\nforce_type\x18\x02 \x02(\x0e\x32\x11.island.ForceType\x12\t\n\x01x\x18\x03 \x02(\x02\x12\t\n\x01y\x18\x04 \x02(\x02\x12\x12\n\nsrc_island\x18\x05 \x02(\x05\x12\x12\n\ndst_island\x18\x06 \x02(\x05\x12\x0b\n\x03uid\x18\x07 \x02(\x05\x12\x0e\n\x06troops\x18\x08 \x02(\x02\x12\x0e\n\x06morale\x18\t \x02(\x02\x12(\n\tmove_type\x18\n \x02(\x0e\x32\x15.island.ForceMoveType\x12\x13\n\x0b\x63reate_time\x18\x0b \x02(\x03\x12\x0e\n\x06radius\x18\x0c \x02(\x02\x12\r\n\x05speed\x18\r \x02(\x02\x12\x14\n\x0cline_segment\x18\x0e \x02(\x05\x12\x12\n\nis_removed\x18\x0f \x02(\x08\"\x8d\x01\n\tGameWorld\x12\r\n\x05width\x18\x01 \x02(\x05\x12\x0e\n\x06height\x18\x02 \x02(\x05\x12\x1f\n\x07islands\x18\x03 \x03(\x0b\x32\x0e.island.Island\x12\x1d\n\x06\x66orces\x18\x04 \x03(\x0b\x32\r.island.Force\x12!\n\x05lines\x18\x05 \x03(\x0b\x32\x12.island.FlightLine\"c\n\nFlightLine\x12\n\n\x02id\x18\x01 \x02(\x05\x12\x12\n\nsrc_island\x18\x02 \x02(\x05\x12\x12\n\ndst_island\x18\x03 \x02(\x05\x12!\n\x06points\x18\x04 \x03(\x0b\x32\x11.island.LinePoint\"&\n\x08Property\x12\x0b\n\x03key\x18\x01 \x02(\x05\x12\r\n\x05value\x18\x02 \x02(\t\"!\n\tLinePoint\x12\t\n\x01x\x18\x01 \x02(\x05\x12\t\n\x01y\x18\x02 \x02(\x05\")\n\x0bPlayerPower\x12\x0b\n\x03uid\x18\x01 \x02(\x05\x12\r\n\x05power\x18\x02 \x02(\x05\x42 \n\x14\x63om.box.island.protoB\x06StructH\x03')
  ,
  dependencies=[constant__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_GAMESERVER = _descriptor.Descriptor(
  name='GameServer',
  full_name='island.GameServer',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='island.GameServer.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ip', full_name='island.GameServer.ip', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='port', full_name='island.GameServer.port', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=40,
  serialized_end=90,
)


_PLAYER = _descriptor.Descriptor(
  name='Player',
  full_name='island.Player',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uid', full_name='island.Player.uid', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='team', full_name='island.Player.team', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='color', full_name='island.Player.color', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='island.Player.name', index=3,
      number=4, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='commander', full_name='island.Player.commander', index=4,
      number=5, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='is_online', full_name='island.Player.is_online', index=5,
      number=7, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='power', full_name='island.Player.power', index=6,
      number=8, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=93,
  serialized_end=229,
)


_COMMANDER = _descriptor.Descriptor(
  name='Commander',
  full_name='island.Commander',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cid', full_name='island.Commander.cid', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='island.Commander.name', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='properties', full_name='island.Commander.properties', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=231,
  serialized_end=307,
)


_GAMESTATE = _descriptor.Descriptor(
  name='GameState',
  full_name='island.GameState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='game_id', full_name='island.GameState.game_id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='players', full_name='island.GameState.players', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=309,
  serialized_end=370,
)


_ISLAND = _descriptor.Descriptor(
  name='Island',
  full_name='island.Island',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='island.Island.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='island_type', full_name='island.Island.island_type', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='x', full_name='island.Island.x', index=2,
      number=3, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='y', full_name='island.Island.y', index=3,
      number=4, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_troops', full_name='island.Island.max_troops', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='radius', full_name='island.Island.radius', index=5,
      number=6, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gun_radius', full_name='island.Island.gun_radius', index=6,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gun_life', full_name='island.Island.gun_life', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=373,
  serialized_end=530,
)


_FORCE = _descriptor.Descriptor(
  name='Force',
  full_name='island.Force',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='island.Force.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='force_type', full_name='island.Force.force_type', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='x', full_name='island.Force.x', index=2,
      number=3, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='y', full_name='island.Force.y', index=3,
      number=4, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='src_island', full_name='island.Force.src_island', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dst_island', full_name='island.Force.dst_island', index=5,
      number=6, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='uid', full_name='island.Force.uid', index=6,
      number=7, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='troops', full_name='island.Force.troops', index=7,
      number=8, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='morale', full_name='island.Force.morale', index=8,
      number=9, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='move_type', full_name='island.Force.move_type', index=9,
      number=10, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='create_time', full_name='island.Force.create_time', index=10,
      number=11, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='radius', full_name='island.Force.radius', index=11,
      number=12, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='speed', full_name='island.Force.speed', index=12,
      number=13, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='line_segment', full_name='island.Force.line_segment', index=13,
      number=14, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='is_removed', full_name='island.Force.is_removed', index=14,
      number=15, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=533,
  serialized_end=834,
)


_GAMEWORLD = _descriptor.Descriptor(
  name='GameWorld',
  full_name='island.GameWorld',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='width', full_name='island.GameWorld.width', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='height', full_name='island.GameWorld.height', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='islands', full_name='island.GameWorld.islands', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='forces', full_name='island.GameWorld.forces', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lines', full_name='island.GameWorld.lines', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=837,
  serialized_end=978,
)


_FLIGHTLINE = _descriptor.Descriptor(
  name='FlightLine',
  full_name='island.FlightLine',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='island.FlightLine.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='src_island', full_name='island.FlightLine.src_island', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dst_island', full_name='island.FlightLine.dst_island', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='points', full_name='island.FlightLine.points', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=980,
  serialized_end=1079,
)


_PROPERTY = _descriptor.Descriptor(
  name='Property',
  full_name='island.Property',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='island.Property.key', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='island.Property.value', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1081,
  serialized_end=1119,
)


_LINEPOINT = _descriptor.Descriptor(
  name='LinePoint',
  full_name='island.LinePoint',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='x', full_name='island.LinePoint.x', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='y', full_name='island.LinePoint.y', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1121,
  serialized_end=1154,
)


_PLAYERPOWER = _descriptor.Descriptor(
  name='PlayerPower',
  full_name='island.PlayerPower',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uid', full_name='island.PlayerPower.uid', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='power', full_name='island.PlayerPower.power', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1156,
  serialized_end=1197,
)

_PLAYER.fields_by_name['commander'].message_type = _COMMANDER
_COMMANDER.fields_by_name['properties'].message_type = _PROPERTY
_GAMESTATE.fields_by_name['players'].message_type = _PLAYER
_ISLAND.fields_by_name['island_type'].enum_type = constant__pb2._ISLANDTYPE
_FORCE.fields_by_name['force_type'].enum_type = constant__pb2._FORCETYPE
_FORCE.fields_by_name['move_type'].enum_type = constant__pb2._FORCEMOVETYPE
_GAMEWORLD.fields_by_name['islands'].message_type = _ISLAND
_GAMEWORLD.fields_by_name['forces'].message_type = _FORCE
_GAMEWORLD.fields_by_name['lines'].message_type = _FLIGHTLINE
_FLIGHTLINE.fields_by_name['points'].message_type = _LINEPOINT
DESCRIPTOR.message_types_by_name['GameServer'] = _GAMESERVER
DESCRIPTOR.message_types_by_name['Player'] = _PLAYER
DESCRIPTOR.message_types_by_name['Commander'] = _COMMANDER
DESCRIPTOR.message_types_by_name['GameState'] = _GAMESTATE
DESCRIPTOR.message_types_by_name['Island'] = _ISLAND
DESCRIPTOR.message_types_by_name['Force'] = _FORCE
DESCRIPTOR.message_types_by_name['GameWorld'] = _GAMEWORLD
DESCRIPTOR.message_types_by_name['FlightLine'] = _FLIGHTLINE
DESCRIPTOR.message_types_by_name['Property'] = _PROPERTY
DESCRIPTOR.message_types_by_name['LinePoint'] = _LINEPOINT
DESCRIPTOR.message_types_by_name['PlayerPower'] = _PLAYERPOWER

GameServer = _reflection.GeneratedProtocolMessageType('GameServer', (_message.Message,), dict(
  DESCRIPTOR = _GAMESERVER,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.GameServer)
  ))
_sym_db.RegisterMessage(GameServer)

Player = _reflection.GeneratedProtocolMessageType('Player', (_message.Message,), dict(
  DESCRIPTOR = _PLAYER,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.Player)
  ))
_sym_db.RegisterMessage(Player)

Commander = _reflection.GeneratedProtocolMessageType('Commander', (_message.Message,), dict(
  DESCRIPTOR = _COMMANDER,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.Commander)
  ))
_sym_db.RegisterMessage(Commander)

GameState = _reflection.GeneratedProtocolMessageType('GameState', (_message.Message,), dict(
  DESCRIPTOR = _GAMESTATE,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.GameState)
  ))
_sym_db.RegisterMessage(GameState)

Island = _reflection.GeneratedProtocolMessageType('Island', (_message.Message,), dict(
  DESCRIPTOR = _ISLAND,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.Island)
  ))
_sym_db.RegisterMessage(Island)

Force = _reflection.GeneratedProtocolMessageType('Force', (_message.Message,), dict(
  DESCRIPTOR = _FORCE,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.Force)
  ))
_sym_db.RegisterMessage(Force)

GameWorld = _reflection.GeneratedProtocolMessageType('GameWorld', (_message.Message,), dict(
  DESCRIPTOR = _GAMEWORLD,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.GameWorld)
  ))
_sym_db.RegisterMessage(GameWorld)

FlightLine = _reflection.GeneratedProtocolMessageType('FlightLine', (_message.Message,), dict(
  DESCRIPTOR = _FLIGHTLINE,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.FlightLine)
  ))
_sym_db.RegisterMessage(FlightLine)

Property = _reflection.GeneratedProtocolMessageType('Property', (_message.Message,), dict(
  DESCRIPTOR = _PROPERTY,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.Property)
  ))
_sym_db.RegisterMessage(Property)

LinePoint = _reflection.GeneratedProtocolMessageType('LinePoint', (_message.Message,), dict(
  DESCRIPTOR = _LINEPOINT,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.LinePoint)
  ))
_sym_db.RegisterMessage(LinePoint)

PlayerPower = _reflection.GeneratedProtocolMessageType('PlayerPower', (_message.Message,), dict(
  DESCRIPTOR = _PLAYERPOWER,
  __module__ = 'struct_pb2'
  # @@protoc_insertion_point(class_scope:island.PlayerPower)
  ))
_sym_db.RegisterMessage(PlayerPower)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\024com.box.island.protoB\006StructH\003'))
# @@protoc_insertion_point(module_scope)
