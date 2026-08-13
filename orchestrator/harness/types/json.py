
type JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
type JSONObject = dict[str, JSON]
type JSONArray = list[JSON]
