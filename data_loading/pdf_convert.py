from pathlib import Path
import pdfkit

quarter = ['Q1', 'Q2', 'Q3', 'Q4']
ticker = ['CSGP', 'CEG', 'MU', 'CTSH', 'PEP', 'PYPL', 'TMUS', 'ISRG', 'CSCO', 
        'AMD', 'ADSK', 'FAST', 'ILMN', 'CPRT', 'CHTR', 'KHC', 'BKNG', 'MDB', 
        'META', 'ABNB', 'FANG', 'PCAR', 'EA', 'AVGO', 'MDLZ', 'ORLY', 'FI', 
        'GEHC', 'GOOGL', 'REGN', 'ADBE', 'BKR', 'KLAC', 'LULU', 'PAYX', 'XEL',
        'SPLK', 'AEP', 'ROST', 'QCOM', 'EXC', 'BIIB', 'LRCX', 'MSFT', 'GILD', 
        'CMCSA', 'VRSK', 'IDXX', 'DDOG', 'AMAT', 'TXN', 'INTU', 'SNPS', 'CTAS', 
        'DXCM', 'MRNA', 'VRTX', 'ANSS', 'COST', 'ZS', 'FTNT', 'ODFL', 'CRWD', 
        'ADI', 'AAPL', 'AMGN', 'MCHP', 'CSX', 'CDW', 'SBUX', 'MAR', 'DLTR', 
        'NXPI', 'GOOG', 'KDP', 'TSLA', 'NFLX', 'NVDA', 'INTC', 'TEAM', 'MRVL', 
        'ADP', 'WDAY', 'TTD', 'CDNS', 'ROP', 'MNST', 'PANW', 'HON', 'WBD', 'MELI', 
        'AMZN', 'WBA', 'DASH', 'ON', 'SIRI']
for q in quarter:
    for tick in ticker:
        filing_doc = Path(f'content/{tick}-{q}-2023.html')
        filing_pdf = Path(f'content_pdf/{tick}-{q}-2023.pdf')
        if filing_doc.exists() and not filing_pdf.exists():
            print("- Converting {}".format(filing_doc))
            input_path = str(filing_doc.absolute())
            output_path = str(filing_pdf.absolute())
            try:
                pdfkit.from_file(input_path, output_path, verbose=True)
            except Exception as e:
                print(f"Error converting {input_path} to {output_path}: {e}")