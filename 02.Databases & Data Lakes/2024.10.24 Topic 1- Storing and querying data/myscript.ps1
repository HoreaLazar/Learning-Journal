$directory = "C:\Users\laho2188"

Get-ChildItem -Path $directory -Directory | ForEach-Object {
 $folder = $_
 $totalSize = (Get-ChildItem -Path $_.FullName -File | Measure-Object -Property Length -Sum).Sum / 1MB
 "{0} has a total size of {1:N2} MB" -f $folder.Name, $totalSize
} 