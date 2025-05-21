# sprint2/utils.py
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


# Asegúrate de tener instalada la librería: pip install xhtml2pdf o pip install WeasyPrint

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    # Para xhtml2pdf
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()

    # Para WeasyPrint (si decides usarla):
    # from weasyprint import HTML
    # HTML(string=html).write_pdf(result)
    # return result.getvalue()

    return None  # Si hubo un error en la generación del PDF