answer = "HELLO WORLD"

solve_state = ""

for char in answer:
    if char is not " ":
        solve_state += "_"
    solve_state += " "

print(solve_state)
