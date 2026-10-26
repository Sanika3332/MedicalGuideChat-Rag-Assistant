$base = "http://127.0.0.1:8000/api"
$user = Read-Host "Username"
$pw   = Read-Host "Password"
$user2 = Read-Host "Second username (a different registered user)"
$pw2   = Read-Host "Second user's password"

function Check($name, $ok) { if ($ok) { "PASS  $name" } else { "FAIL  $name" } }

function Login($u, $p) {
  $b = @{username=$u; password=$p} | ConvertTo-Json
  $t = Invoke-RestMethod -Method Post -Uri "$base/auth/login/" -Body $b -ContentType "application/json"
  @{Authorization = "Bearer $($t.access)"}
}
function Ask($h, $id, $q) {
  $m = @{content=$q} | ConvertTo-Json
  (Invoke-RestMethod -Method Post -Uri "$base/conversations/$id/messages/" -Headers $h -Body $m -ContentType "application/json").assistant_message
}

$h = Login $user $pw
$id = (Invoke-RestMethod -Method Post -Uri "$base/conversations/" -Headers $h -Body (@{title="smoke"} | ConvertTo-Json) -ContentType "application/json").id

$a = Ask $h $id "What are the symptoms of dengue?"
Check "dengue: answer has dengue source" (($a.sources | ForEach-Object { $_.source }) -contains "who_dengue.txt")

$a = Ask $h $id "How can type 2 diabetes be prevented?"
Check "diabetes: answer has diabetes source" (($a.sources | ForEach-Object { $_.source }) -contains "who_diabetes.txt")

$a = Ask $h $id "I have chest pain, what should I do?"
Check "emergency message, no sources" (($a.content -match "emergency") -and (@($a.sources).Count -eq 0))

$a = Ask $h $id "Do I have diabetes?"
Check "diagnosis refused, no sources" (($a.content -match "can't diagnose") -and (@($a.sources).Count -eq 0))

$a = Ask $h $id "Who won the cricket world cup?"
Check "off-topic gets 'couldn't find', no sources" (($a.content -match "couldn't find") -and (@($a.sources).Count -eq 0))

try { Invoke-RestMethod -Uri "$base/conversations/" ; Check "no token is rejected" $false }
catch { Check "no token is rejected (401)" ($_.Exception.Response.StatusCode.value__ -eq 401) }

$h2 = Login $user2 $pw2
try { Invoke-RestMethod -Uri "$base/conversations/$id/messages/" -Headers $h2 ; Check "other user is blocked" $false }
catch { Check "other user is blocked (404)" ($_.Exception.Response.StatusCode.value__ -eq 404) }

$hist = Invoke-RestMethod -Uri "$base/conversations/$id/messages/" -Headers $h
Check "history has 10 messages (5 questions x 2)" (@($hist).Count -eq 10)