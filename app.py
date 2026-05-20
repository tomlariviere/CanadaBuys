from flask import Flask, request, render_template_string
import pandas as pd

# Load the CSV file
#df = pd.read_csv("contractHistoryComplete-contratsOctroyesComplet.csv", low_memory=False)
df1 = pd.read_csv("contractHistoryComplete-contratsOctroyesComplet.csv", low_memory=False)
df2 = pd.read_csv("2009-2023-contractHistoryHistorical-contratsOctroyesHistorique.csv", low_memory=False)

# Combine them
df = pd.concat([df1, df2], ignore_index=True)

# Columns to display in the specified order
columns_to_display = [
    "contractNumber-numeroContrat",  # F
    "supplierLegalName-nomLegalFournisseur-eng",  # A
    "endUserEntitiesName-nomEntitesUtilisateurFinal-eng",  # AQ
    "contractAwardDate-dateAttributionContrat",  # I
    "contractEndDate-dateFinContrat",
    "contractAmount-montantContrat",
    "totalContractValue-valeurTotaleContrat",
    "gsinDescription-nibsDescription-eng"  # R
]

# Friendly names for columns
column_labels = {
    "contractNumber-numeroContrat": "Contract Number",
    "supplierLegalName-nomLegalFournisseur-eng": "Company",
    "endUserEntitiesName-nomEntitesUtilisateurFinal-eng": "GOC Client",
    "contractAwardDate-dateAttributionContrat": "Contract Award Date",
    "contractEndDate-dateFinContrat": "Contract End Date",
    "contractAmount-montantContrat": "Contract Amount",
    "totalContractValue-valeurTotaleContrat": "Contract Value",
    "gsinDescription-nibsDescription-eng": "Description"
}

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Tom's Totally Not CanadaBuys Query Tool</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .no-results { color: red; font-weight: bold; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Tom's Totally Not CanadaBuys Query Tool</h1>
    <form method="POST">
        <input type="text" name="search_term" placeholder="Enter search term" style="width:300px;">
        <select name="sort_by">
            <option value="">Sort by...</option>
            {% for col in columns %}
                <option value="{{ col }}">{{ column_labels[col] }}</option>
            {% endfor %}
        </select>
        <select name="order">
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
        </select>
        <button type="submit">Search</button>
    </form>
    {% if results %}
        <h2>Found {{ results|length }} matching rows:</h2>
        <table>
            <tr>
                {% for col in columns %}
                    <th>{{ column_labels[col] }}</th>
                {% endfor %}
            </tr>
            {% for row in results %}
                <tr>
                    {% for col in columns %}
                        <td style="text-align: {% if col in ['contractAmount-montantContrat', 
                        'totalContractValue-valeurTotaleContrat'] %}right{% else %}left{% endif %};">
                            {{ row[col] }}
                        </td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </table>
    {% elif searched %}
        <div class="no-results">No results found for "{{ search_term }}".</div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    searched = False
    search_term = ""
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        sort_by = request.form.get('sort_by')
        order = request.form.get('order')
        searched = True
        if search_term:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
            filtered = df[mask]
            # Apply sorting if selected
            if sort_by in columns_to_display:
                filtered = filtered.sort_values(by=sort_by, ascending=(order == 'asc'))
            # Apply formatting for dollar values
            for col in ["contractAmount-montantContrat", "totalContractValue-valeurTotaleContrat"]:
                filtered[col] = pd.to_numeric(filtered[col], errors='coerce')  # ensure numeric
                filtered[col] = filtered[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")

            results = filtered[columns_to_display].to_dict(orient='records')    
            #results = filtered[columns_to_display].to_dict(orient='records')
    return render_template_string(HTML_TEMPLATE, results=results, columns=columns_to_display,
                                  column_labels=column_labels, searched=searched, search_term=search_term)

if __name__ == '__main__':
    app.run(debug=True)
