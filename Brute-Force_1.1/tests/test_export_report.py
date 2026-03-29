import unittest
from tools.export_report import generar_reporte_pdf
import os

class TestExportReport(unittest.TestCase):
    def test_generar_pdf(self):
        test_csv = 'test_result.csv'
        test_pdf = 'test_report.pdf'
        with open(test_csv, 'w') as f:
            f.write('Usuario,Password,Resultado\nadmin,admin,OK\n')
        generar_reporte_pdf(test_csv, test_pdf, resumen="Resumen de prueba")
        self.assertTrue(os.path.isfile(test_pdf))
        os.remove(test_csv)
        os.remove(test_pdf)
