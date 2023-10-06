css = """
<style>
#table {
    width: 100%;
    border-collapse: collapse;
}

#table th,
#table td {
text-color: white;
border: 1px solid white;
padding: 5px;
}

#table th {
background-color: #4CAF50;
}
</style>
"""
table_template = """
<table id="table">
<tr>
  <td>{{Rank}}</td>
  <td>{{Name}}</td>
  <td>{{Match}}</td>
</tr>
</table>
"""

# <thead>
# <tr>
# <th>Rank</th>
# <th>Name</th>
# <th>Match</th>
# </tr>
# </thead>