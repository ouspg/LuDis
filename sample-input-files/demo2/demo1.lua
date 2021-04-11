-- Dissector for DEMO1 --
local proto = Proto("DEMO1", "DEMO1 Test Protocol")

-- Protocol field definitions --
local fields = proto.fields
fields.f1 = ProtoField.uint8("proto.f0", "Message ID", nil, nil, nil, nil)
fields.f2 = ProtoField.uint16("proto.f1", "Payload length", base_DEC, nil, nil, nil)
fields.f3 = ProtoField.bytes("proto.f2", "Source info", nil, nil, nil, "Information about the sender")
local f3_s1_valstr = { [443] = "HTTPS", [22] = "SSH", }
fields.f3_s1 = ProtoField.uint16("proto.sf2-0", "Source port", base_DEC, f3_s1_valstr, nil, nil)
fields.f3_s2 = ProtoField.ipv4("proto.sf2-1", "Source IP", nil, nil, nil, nil)
fields.f4 = ProtoField.bytes("proto.f3", "Destination info", nil, nil, nil, "Information about the receiver")
local f4_s1_valstr = { [443] = "HTTPS", [22] = "SSH", }
fields.f4_s1 = ProtoField.uint16("proto.sf3-0", "Destination port", base_DEC, f4_s1_valstr, nil, nil)
fields.f4_s2 = ProtoField.ipv4("proto.sf3-1", "Destination IP", nil, nil, nil, nil)
fields.payload = ProtoField.string("proto.payload", "Payload")

-- Dissector function --
function proto.dissector(buffer, pinfo, tree)

	local subtree = tree:add(proto, buffer())
	pinfo.cols.protocol = proto.name
	pinfo.cols.info = proto.description

	local packet = buffer():string()
	subtree:add(fields.f1, buffer(0,1))
	subtree:add(fields.f2, buffer(1,2))
	local subsubtree_f3 = subtree:add(fields.f3, buffer(3,6))
	subsubtree_f3:add(fields.f3_s1, buffer(3,2))
	subsubtree_f3:add(fields.f3_s2, buffer(5,4))
	local subsubtree_f4 = subtree:add(fields.f4, buffer(9,6))
	subsubtree_f4:add(fields.f4_s1, buffer(9,2))
	subsubtree_f4:add(fields.f4_s2, buffer(11,4))

	-- Handle the payload --
	local payload_length = buffer(1,2):uint()
	subtree:add(fields.payload, buffer(15, payload_length))

end

-- Dissector registration --
local parent_dt = DissectorTable.get("udp.port")
parent_dt:add(55555, proto)
