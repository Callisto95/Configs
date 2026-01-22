#!/usr/bin/nu

def sort_js [] {
    open user.js | lines | sort | save -f user.js
}

def main []: nothing -> nothing {
    sort_js;
}

def "main add" [key: string, value: any]: nothing -> nothing {
    let realValue = if ($value | describe ) == "string" {
        $"\"($value)\""
    } else {
        $value
    }
    
    open user.js | lines | append $"user_pref\(\"($key)\", ($value)\)" | sort | save -f user.js;
}
