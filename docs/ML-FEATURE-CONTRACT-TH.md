# ML Feature Contract สำหรับ Scanner

เอกสารนี้บอกว่า scanner/feature extractor ต้องส่ง feature แบบไหนให้ ML runtime

## หลักการสำคัญ

Feature ที่ส่งเข้า ML runtime ต้องเป็นข้อมูลที่รู้ได้ก่อน exploit verification

ใช้ได้:

- fingerprint product
- version range
- auth required หรือไม่
- endpoint reachable หรือ missing
- port open หรือ closed
- config/path/precondition probe

ไม่ควรใช้:

- exploit สำเร็จแล้วหรือไม่
- Metasploit check confirmed
- manual PoC result
- flag หรือ shell result

## Required Shape

Input เป็น JSON object แบน ๆ ไม่มี nested object

```json
{
  "target_id": "example_target",
  "redis_detected": 1,
  "auth_required": 0,
  "no_auth_required": 1,
  "version_in_vulnerable_range": 1
}
```

ค่า feature ควรเป็น:

```text
1 = true / พบ / ใช่
0 = false / ไม่พบ / ไม่ใช่
```

ถ้าไม่รู้ ให้ไม่ส่ง field นั้น หรือส่งเป็น 0

## Common Feature Groups

Version:

```text
version_in_vulnerable_range
version_in_vulnerable_range_true
version_in_vulnerable_range_false
version_not_affected
version_patched
wrong_version
```

Auth:

```text
auth_required
no_auth_required
anonymous_access
auth_blocks_exploit
```

Endpoint:

```text
endpoint_reachable_count
endpoint_missing_count
endpoint_not_found
config_accessible
config_blocked
config_api_accessible
config_api_blocked
```

Unknown family:

```text
unknown_product_detected
unknown_family_signal_count
known_family_signal_count
```

## Family-specific Examples

Redis positive:

```json
{
  "target_id": "redis_positive_example",
  "redis_detected": 1,
  "redis_info_accessible": 1,
  "lua_available": 1,
  "auth_required": 0,
  "no_auth_required": 1,
  "version_in_vulnerable_range": 1,
  "known_family_signal_count": 2,
  "unknown_family_signal_count": 0,
  "unknown_product_detected": 0
}
```

Redis negative:

```json
{
  "target_id": "redis_negative_example",
  "redis_detected": 1,
  "redis_info_accessible": 0,
  "lua_available": 0,
  "auth_required": 1,
  "no_auth_required": 0,
  "version_in_vulnerable_range": 1,
  "known_family_signal_count": 0,
  "unknown_family_signal_count": 0,
  "unknown_product_detected": 0
}
```

Tomcat PUT positive:

```json
{
  "target_id": "tomcat_put_positive_example",
  "tomcat_detected": 1,
  "method_put_allowed": 1,
  "method_put_rejected": 0,
  "jsp_upload_candidate": 1,
  "upload_blocked": 0,
  "version_in_vulnerable_range": 1
}
```

Tomcat PUT negative:

```json
{
  "target_id": "tomcat_put_negative_example",
  "tomcat_detected": 1,
  "method_put_allowed": 0,
  "method_put_rejected": 1,
  "jsp_upload_candidate": 0,
  "upload_blocked": 1,
  "version_patched": 1
}
```

Solr Velocity positive:

```json
{
  "target_id": "solr_velocity_positive_example",
  "solr_detected": 1,
  "solr_core_found": 1,
  "velocity_enabled": 1,
  "velocity_disabled": 0,
  "velocity_endpoint_found": 1,
  "velocity_template_accessible": 1,
  "config_api_accessible": 1,
  "config_api_blocked": 0,
  "version_in_vulnerable_range": 1
}
```

Solr Velocity negative:

```json
{
  "target_id": "solr_velocity_negative_example",
  "solr_detected": 1,
  "solr_core_found": 1,
  "velocity_enabled": 0,
  "velocity_disabled": 1,
  "velocity_endpoint_found": 0,
  "velocity_template_accessible": 0,
  "config_api_accessible": 1,
  "version_in_vulnerable_range": 1
}
```

CouchDB positive:

```json
{
  "target_id": "couchdb_positive_example",
  "couchdb_detected": 1,
  "admin_party_enabled": 1,
  "auth_required": 0,
  "no_auth_required": 1,
  "config_accessible": 1,
  "users_db_accessible": 1,
  "version_in_vulnerable_range": 1
}
```

CouchDB negative:

```json
{
  "target_id": "couchdb_negative_example",
  "couchdb_detected": 1,
  "admin_party_enabled": 0,
  "auth_required": 1,
  "no_auth_required": 0,
  "config_accessible": 0,
  "config_blocked": 1,
  "users_db_accessible": 0
}
```

## Output Contract สำหรับ LLM

Scanner/agent ควรส่ง output จาก ML ให้ LLM โดยไม่ตัด field สำคัญออก:

```text
target_id
gate.score
gate.threshold
gate.decision
ranker.decision
ranker.top_families
final_decision
recommended_next_action
reason_features
schema_warnings
safety_note_th
```

LLM ควรใช้ `final_decision` เป็นตัวคุม behavior หลัก ไม่ใช้ `gate.score` อย่างเดียว

