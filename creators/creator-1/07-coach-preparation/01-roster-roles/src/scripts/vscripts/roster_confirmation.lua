-- Server-owned compatibility for five TEST profiles; no runtime/engine effects.
local R={}
local definitions={
 ['TEST-player-001']={heroes={npc_dota_hero_crystal_maiden=true,npc_dota_hero_lion=true},roles={[4]=true,[5]=true},coverage=.8},
 ['TEST-player-002']={heroes={npc_dota_hero_juggernaut=true,npc_dota_hero_sven=true},roles={[1]=true},coverage=.2},
 ['TEST-player-003']={heroes={npc_dota_hero_lina=true,npc_dota_hero_storm_spirit=true},roles={[2]=true},coverage=.7},
 ['TEST-player-004']={heroes={npc_dota_hero_axe=true,npc_dota_hero_centaur=true},roles={[3]=true},coverage=.9},
 ['TEST-player-005']={heroes={npc_dota_hero_lion=true,npc_dota_hero_shadow_shaman=true},roles={[4]=true,[5]=true},coverage=.6},
}
local default={
 {projectId='TEST-player-001',hero='npc_dota_hero_crystal_maiden',role=5},
 {projectId='TEST-player-002',hero='npc_dota_hero_juggernaut',role=1},
 {projectId='TEST-player-003',hero='npc_dota_hero_lina',role=2},
 {projectId='TEST-player-004',hero='npc_dota_hero_axe',role=3},
 {projectId='TEST-player-005',hero='npc_dota_hero_lion',role=4},
}
local function exact(t,fields,count)
 if type(t)~='table' or getmetatable(t)~=nil then return false end
 local n=0;for k in pairs(t)do if not fields[k]then return false end;n=n+1 end
 return n==count
end
function R.default_assignments()
 local out={};for i,e in ipairs(default)do out[i]={projectId=e.projectId,hero=e.hero,role=e.role}end;return out
end
function R.server_profiles()
 local out={};for id,d in pairs(definitions)do out[id]={coverage=d.coverage,synthetic=true}end;return out
end
function R.confirm(assignments,profiles)
 local numeric={[1]=true,[2]=true,[3]=true,[4]=true,[5]=true}
 if not exact(assignments,numeric,5) or not exact(profiles,definitions,5)then return nil,'invalid_request' end
 for pid in pairs(definitions)do
  local p=profiles[pid]
  if not exact(p,{coverage=true,synthetic=true},2) or p.synthetic~=true or type(p.coverage)~='number'
    or p.coverage~=p.coverage or p.coverage<0 or p.coverage>1 then return nil,'invalid_request' end
 end
 local ids,heroes,roles,out={},{},{},{}
 for i=1,5 do
  local e=assignments[i]
  if not exact(e,{projectId=true,hero=true,role=true},3) or type(e.projectId)~='string' or type(e.hero)~='string'
    or type(e.role)~='number' or e.role%1~=0 or e.role<1 or e.role>5 then return nil,'invalid_request' end
  local d=definitions[e.projectId]
  if d==nil or not d.heroes[e.hero] or not d.roles[e.role] or ids[e.projectId] or heroes[e.hero] or roles[e.role]then return nil,'invalid_request' end
  ids[e.projectId]=true;heroes[e.hero]=true;roles[e.role]=true
  local coverage=profiles[e.projectId].coverage
  out[tostring(i)]={id=e.projectId,hero=e.hero,role=e.role,coverage=coverage,warning=coverage<.5 and 'weak-coverage' or ''}
 end
 return {synthetic=1,assignments=out},'none'
end
return R
