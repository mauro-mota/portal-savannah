from datetime import timedelta
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from .models import User, Task, Event, Goal, Notice
from .forms import EventForm, GoalForm
@override_settings(STORAGES={"default":{"BACKEND":"django.core.files.storage.FileSystemStorage"},"staticfiles":{"BACKEND":"django.contrib.staticfiles.storage.StaticFilesStorage"}})
class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.a=User.objects.create_user('ana',password='SenhaTesteLonga123!')
        cls.b=User.objects.create_user('bruno',password='OutraSenhaLonga123!')
        cls.c=User.objects.create_user('carla',password='TerceiraSenha123!')
        cls.admin=User.objects.create_superuser('gestor',password='SenhaGestorLonga123!')
        cls.task=Task.objects.create(title='Entregar relatório',created_by=cls.a,assignee=cls.b,due_date=timezone.localdate())
        cls.event=Event.objects.create(title='Reunião da equipe',created_by=cls.a,start=timezone.now(),end=timezone.now()+timedelta(hours=1))
        cls.goal=Goal.objects.create(title='Entregas do mês',created_by=cls.a,owner=cls.b,target=10,current=3,due_date=timezone.localdate())
        cls.notice=Notice.objects.create(title='Aviso interno',created_by=cls.admin)
    def test_anonymous_is_redirected_from_every_module(self):
        for url in ['/', '/tarefas/', '/compromissos/', '/calendario/', '/metas/', '/comunicados/', '/tarefas/novo/']:
            self.assertEqual(self.client.get(url).status_code,302)
    def test_login_and_logout(self):
        self.assertEqual(self.client.post('/entrar/',{'username':'ana','password':'SenhaTesteLonga123!'}).status_code,302)
        self.assertEqual(self.client.get('/').status_code,200)
        self.assertEqual(self.client.get('/sair/').status_code,405)
        self.assertEqual(self.client.post('/sair/').status_code,302)
        self.assertEqual(self.client.get('/').status_code,302)
    def test_all_shared_pages_render_for_employee(self):
        self.client.force_login(self.c)
        for url in ['/', '/tarefas/', '/compromissos/', '/calendario/', '/metas/', '/comunicados/', '/senha/']:
            self.assertEqual(self.client.get(url).status_code,200,url)
        self.assertContains(self.client.get('/tarefas/'),'Entregar relatório')
        self.assertEqual(self.client.get('/admin/').status_code,302)
    def test_unrelated_employee_cannot_modify_even_by_direct_post(self):
        self.client.force_login(self.c)
        for kind,obj in [('tarefas',self.task),('compromissos',self.event),('metas',self.goal),('comunicados',self.notice)]:
            for action in ['editar','excluir']:
                url=f'/{kind}/{obj.pk}/{action}/'
                self.assertEqual(self.client.get(url).status_code,403)
                self.assertEqual(self.client.post(url,{'title':'Alterado'}).status_code,403)
        self.assertEqual(self.client.post('/comunicados/novo/',{'title':'Sem permissão'}).status_code,403)
    def test_assignee_updates_task(self):
        self.client.force_login(self.b)
        result=self.client.post(f'/tarefas/{self.task.pk}/editar/',{'title':self.task.title,'assignee':self.b.pk,'due_date':str(timezone.localdate()),'status':'done','priority':'normal','notes':'Finalizado'})
        self.assertEqual(result.status_code,302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status,'done')
        self.assertEqual(self.task.created_by,self.a)
    def test_creator_is_not_taken_from_post(self):
        self.client.force_login(self.c)
        result=self.client.post('/tarefas/novo/',{'title':'Nova tarefa','assignee':self.b.pk,'due_date':str(timezone.localdate()),'status':'todo','priority':'normal','created_by':self.admin.pk})
        self.assertEqual(result.status_code,302)
        self.assertEqual(Task.objects.get(title='Nova tarefa').created_by,self.c)
    def test_delete_requires_post_and_authorization(self):
        self.client.force_login(self.a)
        url=f'/tarefas/{self.task.pk}/excluir/'
        self.assertEqual(self.client.get(url).status_code,200)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())
        self.assertEqual(self.client.post(url).status_code,302)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
    def test_csrf_enforced_for_mutations(self):
        c=Client(enforce_csrf_checks=True);c.force_login(self.a)
        self.assertEqual(c.post(f'/tarefas/{self.task.pk}/excluir/').status_code,403)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())
    def test_invalid_dates_and_targets(self):
        start=timezone.now()
        form=EventForm({'title':'Teste','start':start,'end':start-timedelta(hours=1)})
        self.assertFalse(form.is_valid())
        form=GoalForm({'title':'Teste','owner':self.a.pk,'due_date':str(timezone.localdate()),'target':0,'current':-1,'unit':'vendas'})
        self.assertFalse(form.is_valid())
        self.assertEqual(self.goal.percent,30)
    def test_admin_can_edit_all_and_create_notice(self):
        self.client.force_login(self.admin)
        for kind,obj in [('tarefas',self.task),('compromissos',self.event),('metas',self.goal),('comunicados',self.notice)]:
            self.assertEqual(self.client.get(f'/{kind}/{obj.pk}/editar/').status_code,200)
        self.assertEqual(self.client.post('/comunicados/novo/',{'title':'Novo aviso','description':'Informação'}).status_code,302)
    def test_calendar_tolerates_bad_parameter(self):
        self.client.force_login(self.a)
        self.assertEqual(self.client.get('/calendario/?mes=invalido').status_code,200)
        self.assertEqual(self.client.get('/calendario/?mes=9999-12-01').status_code,200)
    def test_inactive_user_cannot_login(self):
        self.a.is_active=False;self.a.save()
        self.client.post('/entrar/',{'username':'ana','password':'SenhaTesteLonga123!'})
        self.assertEqual(self.client.get('/').status_code,302)
    def test_five_bad_passwords_lock_account(self):
        for _ in range(5):
            response=self.client.post('/entrar/',{'username':'ana','password':'errada'})
        self.assertEqual(response.status_code,429)
        response=self.client.post('/entrar/',{'username':'ana','password':'SenhaTesteLonga123!'})
        self.assertEqual(response.status_code,429)
