import django, os, sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django_tenants.utils import schema_context

with schema_context('papeleria'):
    from django.db import connection
    with connection.cursor() as cur:
        cur.execute("""
            SELECT DATE_TRUNC('month', fecha_venta) as mes,
                   COUNT(*) as ventas,
                   SUM(total) as total
            FROM ventas_venta
            GROUP BY DATE_TRUNC('month', fecha_venta)
            ORDER BY mes DESC LIMIT 12
        """)
        print('Mes       | Ventas | Total')
        print('-' * 42)
        for r in cur.fetchall():
            print(f'{str(r[0])[:7]}  |  {r[1]:4d}  | ${float(r[2] or 0):,.2f}')

        cur.execute('SELECT COUNT(*) FROM ventas_ventaitem')
        items = cur.fetchone()[0]
        print(f'\nVentaItems: {items}')

        # Hoy
        from datetime import date
        cur.execute('SELECT COUNT(*), SUM(total) FROM ventas_venta WHERE DATE(fecha_venta) = %s', [date.today()])
        r = cur.fetchone()
        print(f'Hoy: {r[0]} ventas — ${float(r[1] or 0):.2f}')
