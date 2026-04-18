$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

function Get-DotEnvValue {
    param([Parameter(Mandatory = $true)][string]$Key)
    if (-not (Test-Path ".env")) { return $null }
    $line = Get-Content ".env" -ErrorAction SilentlyContinue |
        Where-Object { $_ -match "^\s*$([Regex]::Escape($Key))\s*=" } |
        Select-Object -First 1
    if (-not $line) { return $null }
    $v = ($line -replace "^\s*$([Regex]::Escape($Key))\s*=\s*", "").Trim()
    if ($v.StartsWith('"') -and $v.EndsWith('"')) { $v = $v.Trim('"') }
    return $v
}

$domain = Get-DotEnvValue "DOMAIN"
$email = Get-DotEnvValue "CERTBOT_EMAIL"

if (-not $domain -or $domain -eq "_") {
    Write-Error "Set DOMAIN in .env to your public hostname (not _)."
}
if (-not $email) {
    Write-Error "Set CERTBOT_EMAIL in .env for Let's Encrypt."
}

docker compose up -d web nginx

docker compose exec -T nginx certbot certonly `
    --webroot `
    -w /var/www/certbot `
    -d $domain `
    --email $email `
    --agree-tos `
    --no-eff-email `
    --non-interactive

docker compose restart nginx
