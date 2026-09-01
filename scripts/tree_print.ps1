function treex($Path = ".", $Exclude = @(".venv", ".git"), $Prefix = "") {
    $items = Get-ChildItem -LiteralPath $Path -Force |
        Where-Object { $_.Name -notin $Exclude } |
        Sort-Object @{Expression={$_.PSIsContainer};Descending=$true}, Name

    for ($i = 0; $i -lt $items.Count; $i++) {
        $item = $items[$i]
        $last = $i -eq $items.Count - 1
        $branch = if ($last) { "└── " } else { "├── " }

        Write-Output "$Prefix$branch$($item.Name)"

        if ($item.PSIsContainer) {
            $nextPrefix = $Prefix + $(if ($last) { "    " } else { "│   " })
            treex $item.FullName $Exclude $nextPrefix
        }
    }
}