-- Dissector for DEMO4 --
local proto = Proto("DEMO4", "DEMO4 Parent Protocol")
local proto_dt = DissectorTable.new("demo4.port", "DEMO4")

-- Protocol field definitions --
local fields = proto.fields
local f1_valstr = { [194] = "IRC", [6679] = "IRC_DEMO", }
fields.f1 = ProtoField.uint16("proto.f0", "Port", base_DEC, f1_valstr, 0xFFFF00, nil)
fields.f2 = ProtoField.string("proto.f1", "Server", nil, nil, nil, nil)
fields.payload = ProtoField.string("proto.payload", "Payload")

-- Dissector function --
function proto.dissector(buffer, pinfo, tree)

	local subtree = tree:add(proto, buffer())
	pinfo.cols.protocol = proto.name
	pinfo.cols.info = proto.description

	local packet = buffer():string()
	local def_fields = {true,true,}
	local def_subfields = { {}, {}, }
	-- Delimiters --
	local field_delim = ":"
	local subfield_delim = ""
	-- Field variables --
	local field = nil
	local field_delim_start = nil
	local field_delim_end = 1
	local field_start = 1
	local field_num = 1

	-- Search fields separated by the field delimiter --
	repeat
		if field_delim:len() > 0 then
			field_delim_start, field_delim_end = packet:find(field_delim, field_delim_end)
		end
		if field_delim_start ~= nil then
			field = packet:sub(field_start, field_delim_end)
			local subsubtree = nil
			if def_fields[field_num] then
				subsubtree = subtree:add(fields["f"..field_num], buffer(field_start-1, field:len()))
			end
			-- Subfield variables --
			local subfield = nil
			local subfield_delim_start = nil
			local subfield_delim_end = nil
			local subfield_start = field_start
			local subfield_num = 1

			-- Search subfields separated by the subfield delimiter inside the field --
			repeat
				if not def_fields[field_num] then break end
				if subfield_delim:len() > 0 then
					subfield_delim_start, subfield_delim_end = packet:find(subfield_delim, subfield_start, field_delim_start-1)
				end
				if subfield_delim_start ~= nil and subfield_delim_end < field_delim_start then
					subfield = packet:sub(subfield_start, subfield_delim_start-1)
					if def_subfields[field_num][subfield_num] then
						subsubtree:add(fields["f"..field_num.."_s"..subfield_num], buffer(subfield_start-1, subfield:len()))
					end
					subfield_num = subfield_num + 1
					subfield_start = subfield_delim_end + 1
				elseif subfield_num > 1 and def_subfields[field_num][subfield_num] then
					subfield = packet:sub(subfield_start, field_delim_start-1)
					subsubtree:add(fields["f"..field_num.."_s"..subfield_num], buffer(subfield_start-1, subfield:len()))
				end
			until subfield_delim_start == nil or subfield_delim_end >= field_delim_start

			field_num = field_num + 1
			field_start = field_delim_end + 1
			field_delim_end = field_delim_end + 1
		end
	until field_delim_start == nil

	-- Handle the payload --
	local payload_delim = "\r\n"
	local payload_delim_start = nil
	local payload_delim_end = nil
	payload_delim_start, payload_delim_end = packet:find(payload_delim, 19)
	local subdiss_id = buffer(0,2):uint()
	local payload_start = 18
	proto_dt:try(subdiss_id, buffer(payload_start, (payload_delim_end-1)-payload_start+1):tvb(), pinfo, tree)

end

-- Dissector registration --
local parent_dt = DissectorTable.get("tcp.port")
parent_dt:add(9876, proto)