from django.shortcuts import get_object_or_404, render, redirect
from .forms import ImportedFileForm, ReportForm
from .models import ImportedFile, Report
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from django.http import HttpResponse
from xhtml2pdf import pisa
import os
import re
from django.template.loader import render_to_string


def profile(request):
    return render(request, 'core/profile.html')

def import_file(request):
    if request.method == 'POST':
        form = ImportedFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('core:import_file')
    else:
        form = ImportedFileForm()
    
    imported_files = ImportedFile.objects.all()
    return render(request, 'core/import_file.html', {'form': form, 'imported_files': imported_files})

def delete_file(request, file_id):
    file = get_object_or_404(ImportedFile, id=file_id)
    file.delete()
    return redirect('core:import_file')

def home(request):
    def extraire_informations(fichier, champs_extraire):
        regex_date = r"[A-Z][a-z]{2}\s\d{1,2}"
        regex_heure = r"\d{2}:\d{2}:\d{2}"
        regex_ip_port = r"IP=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})"
        regex_operation = r"\b(ACCEPT|SRCH|BIND|closed|SEARCH|RESULT|TLS)\b"

        informations = []
        data = {}

        with open(fichier, "r") as f:
            for ligne in f:
                for champ in champs_extraire:
                    if champ == "Date":
                        valeur = re.findall(regex_date, ligne)
                        if valeur:
                            data["Date"] = valeur[0]
                            
                    elif champ == "Heure":
                        valeur = re.findall(regex_heure, ligne)
                        if valeur:
                            data["Heure"] = valeur[0]
                            data["Heure_Numerique"] = int(valeur[0].split(":")[0]) 
                    elif champ == "IP":
                        valeur = re.findall(regex_ip_port, ligne)
                        if valeur:
                            data["IP"] = valeur[0][0]
                    elif champ == "Port":
                        valeur = re.findall(regex_ip_port, ligne)
                        if valeur:
                            data["Port"] = valeur[0][1]
                    elif champ == "Type d'Opération":
                        valeur = re.findall(regex_operation, ligne)
                        if valeur:
                            data["Type d'Opération"] = valeur[0]

                if data:
                    informations.append(data)
                    data = {}

        df = pd.DataFrame(informations, columns=champs_extraire + ["Heure_Numerique"])

        return df

    def filtrer_par_date(df, date_debut, date_fin):
        current_year = datetime.now().year
        df["Date_Complète"] = df["Date"] + " " + df["Heure"] + " " + str(current_year)
        df["Date_Complète"] = pd.to_datetime(df["Date_Complète"], format="%b %d %H:%M:%S %Y")
        df["Date_Complète"] = df["Date_Complète"].dt.strftime("%Y-%m-%dT%H:%M")
        mask = (df["Date_Complète"] >= date_debut.strftime("%Y-%m-%dT%H:%M")) & (df["Date_Complète"] <= date_fin.strftime("%Y-%m-%dT%H:%M"))
        return df.loc[mask]
    
    def generer_graphe_connexions_par_heure(df, report_name):
        plt.figure()
        df_count = df["Heure_Numerique"].value_counts().sort_index()
        df_count.plot(kind="bar")
        plt.xlabel("Heure")
        plt.ylabel("Nombre de connexions")
        plt.title("Nombre de connexions par heure")

        image_dir = os.path.join('media', 'reports', 'images')
        os.makedirs(image_dir, exist_ok=True)
        image_path = os.path.join(image_dir, f'{report_name}_par_heure.png')
        plt.savefig(image_path)
        plt.close()
        
        return image_path
    
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
       
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            file_id = request.POST.get('file_id')

            imported_file = ImportedFile.objects.get(id=file_id)
            file_path = imported_file.file.path

            data = extraire_informations(file_path, ["Date", "Heure", "IP", "Port", "Type d'Opération"])
            date_debut = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
            date_fin = datetime.strptime(end_date, "%Y-%m-%dT%H:%M")
            filtered_data = filtrer_par_date(data, date_debut, date_fin)

            if not filtered_data.empty:
                plt.figure()
                df_count = filtered_data["Type d'Opération"].value_counts()
                df_count.plot(kind="bar")
                plt.xlabel("Type d'Opération")
                plt.ylabel("Nombre de connexions")
                plt.title("Nombre de connexions par Type d'Opération")
                image_dir = os.path.join('media', 'reports', 'images')
                image_dir_media = os.path.join('reports', 'images')
                os.makedirs(image_dir, exist_ok=True)
                os.makedirs(image_dir_media, exist_ok=True)
                image_path = os.path.join(image_dir, f'{form.cleaned_data["name"]}.png')
                image_path_media = os.path.join(image_dir_media, f'{form.cleaned_data["name"]}.png')
                plt.savefig(image_path)
                plt.close()

                generer_graphe_connexions_par_heure(filtered_data, form.cleaned_data["name"])
                image_path_par_heure_media = os.path.join('reports', 'images', f'{form.cleaned_data["name"]}_par_heure.png')

                report = form.save(commit=False)
                report.image = image_path_media
                report.image_par_heure = image_path_par_heure_media 
                report.save()

                pdf_path = os.path.join('media', 'reports', f'{report.name}.pdf')
                pdf_path_media = os.path.join('reports', f'{report.name}.pdf')
                pdf_response = HttpResponse(content_type='application/pdf')
                pdf_content = render_to_string('core/report_template.html', {'report': report})
                pisa.CreatePDF(
                    pdf_content,
                    dest=pdf_response
                )
                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_response.content)
                report.file = pdf_path_media
                report.save()

                return redirect('core:reports')
    else:
        form = ReportForm()
    imported_files = ImportedFile.objects.all()
    return render(request, 'core/index.html', {'form': form, 'imported_files': imported_files})

def reports(request):
    reports = Report.objects.all()
    return render(request, 'core/reports.html', {'reports': reports})

def report_details(request, report_id):
    report = Report.objects.get(id=report_id)
    return render(request, 'core/report_details.html', {'report': report})
