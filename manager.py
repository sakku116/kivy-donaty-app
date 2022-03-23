from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from datetime import datetime
from random import randint, sample
from functools import partial

# IMPORT LOCAL MODULES
from screens import FirstScreen, SecondScreen
from widgets import *
from person import Person

def printLog(event, text):
    print(f'({event}) = {text}')

class Manager(Screen):
    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)
        self.bind(size=self.updateLayout)

        # define first screen class
        self._screen1 = FirstScreen()
        self.ids.first_screen_place.add_widget(self._screen1)
        Clock.schedule_once(self.firstScreenSetup)

        # define second screen class
        self._screen2 = SecondScreen()

        # declare people
        self._people = [
            Person('Steven Doe', 'Content Creator', './assets/creators/steven_doe.png'),
            Person('Ze', 'Digital Artist', './assets/creators/ze.jpg'),
            Person('Andre Rio', 'UI/UIX Designer', './assets/creators/andre_rio.jpg'),
            Person('Ky Craft 116', 'Content Creator', './assets/creators/ky_craft_116.jpg'),
            Person('Irwansyah Saputra', 'Influencer', './assets/creators/irwansyah_saputra.jpg'),
            Person('Aspect30', 'Content Creator', './assets/creators/aspect30.jpg'),
            Person('Rayen', 'Digital Artist', './assets/creators/rayen.jpg'),
            Person('Nino', 'Digital Artist', './assets/creators/nino.jpg'),
            Person('Windo Anggara', 'Content Creator', './assets/creators/windo_anggara.jpg')
        ]
        self._selected_person = ''

        self._sidebar_shown_state = False

        # set sidebar screen state
        self.sidebarConfig('for_screen1')

    def updateLayout(self, win, size):
        width, height = size

        sidebar_width = self.ids.sidebar.width

        if width <= 725:
            pass
        else:
            if self._sidebar_shown_state == True:
                # ubah layout dengan mengurangi width dari screens_place
                # dan membuatnya stuck ke kanan (bisa dilakukan karena parentnya adalah floatlayout)
                #self.ids.main_container.width = width-sidebar_width
                Animation(
                    duration = .7,
                    width = width-sidebar_width,
                    t = 'out_circ'
                ).start(self.ids.main_container)
            else:
                self.ids.main_container.width = self.width

    def goToFirstScreen(self, *args):
        def callback(*args):
            screen1_place = self.ids.first_screen_place
            screen1_place.add_widget(self._screen1)
            printLog('log','first_screen created in screen1_place')

            screen2_place = self.ids.second_screen_place
            screen2_place.remove_widget(self._screen2)
            printLog('log','second screen removed from screen2_place')

        self.closeSidebar()

        # menunggu sidebar ditutup selama .2 detik
        Clock.schedule_once(callback, .2)

        # set sidebar screen state
        self.sidebarConfig('for_screen1')

    def goToSecondScreen(self, *args):
        def callback(*args):
            # spawn second_screen
            screen2_place = self.ids.second_screen_place
            screen2_place.add_widget(self._screen2)
            self.secondScreenSetup()

            printLog('log','second_screen created in screen2_place')

            # remove first_screen
            screen1_place = self.ids.first_screen_place
            screen1_place.remove_widget(self._screen1)

            printLog('log','first screen removed from screen1_place')

        if self._sidebar_shown_state == True:
            self.closeSidebar()
            # menunggu sidebar ditutup selama .2 detik
            Clock.schedule_once(callback, .2)
        else:
            Clock.schedule_once(callback)

        # mencegah config berjalan saat proses closeSidebar() berjalan
        Clock.schedule_once(partial(self.sidebarConfig, 'for_screen2'), .2)

    def firstScreenSetup(self, *args):
        # bind tombol yang ada di first_screen karena berbeda parent class dengan manager
        self._screen1.ids.get_started_btn.bind(on_release = self.showLoginForm)
        self._screen1.ids.line_sparator_login_form.bind(on_release = self.removeLoginForm)

    def secondScreenSetup(self, *args):
        # bind send_button
        self._screen2._home_page.ids.donate_card.ids.send_button.bind(on_release = self.sendDonate)

        # setting tanggal
        date = str(datetime.now().strftime('%d/%m/%Y'))
        self._screen2._home_page.ids.donate_card.datetime = date

        # mengacak _people
        self._people = sample(self._people, k=len(self._people))

        # memilih person untuk ditampilkan di donate card
        random_integer = randint(0, len(self._people)-1)
        random_choosen_person = self._people[random_integer]

        self.updateDonateCard(
            random_choosen_person.name,
            random_choosen_person.role,
            random_choosen_person.photo_path
        )

        Clock.schedule_once(self.showLessPeopleSection)

        # bind view all button untuk auto scroll
        self._screen2._home_page.ids.view_all_btn.bind(on_release = self._screen2.scrollToDown)

    def updateDonateCard(self, name, role, pict, *args):
        self._screen2._home_page.ids.donate_card.person_name = name
        self._screen2._home_page.ids.donate_card.person_role = role
        self._screen2._home_page.ids.donate_card.person_pict = pict

        self._selected_person = name

        Clock.schedule_once(self.resetDonateCardForm)

    def resetDonateCardForm(self, *args):
        # mereset form selected_person diperbarui
        self._screen2._home_page.ids.donate_card.ids.money_total.text = '0'
        self._screen2._home_page.ids.donate_card.ids.message_form.text = ''

    def sendDonate(self, *args):
        person = self._screen2._home_page.ids.donate_card.person_name
        money = self._screen2._home_page.ids.donate_card.ids.money_total.text
        message = self._screen2._home_page.ids.donate_card.ids.message_form.text

        if money == '0':
            self.spawnPopup(
                (255/255, 144/255, 144/255, 1),
                'Donasi Gagal!!!',
                f'Setidaknya butuh [color=FFFFFF]$1[/color] untuk berdonasi!!'
            )
        else:
            self.spawnPopup(
                (221/255, 238/255, 170/255, 1),
                'Donasi Berhasil!!!',
                f'Terimakasih, Kamu telah mengirimkan donasi kepada [color=0800EF]{person}[/color] sebesar [color=EC0101]${money}[/color]'
            )
            self.resetDonateCardForm()

        printLog('donate card info', person)
        printLog('donate card info', money)
        printLog('donate card info', message)

    def sidebarConfig(self, screen, *args):
        def spawnItems(menu_items):
            def addItems(*args):
                for i in menu_items:
                    self.ids.sidebar_items_container.add_widget(i)
            task = Clock.schedule_once(addItems)

        self._sidebar_screen_state = screen

        if screen == 'for_screen1':
            printLog('sidebar', 'for screen1')
            # bersihkan menu dari for_screen1
            # menghindari error ketika sidebar_place belum ditempati
            if len(self.ids.sidebar_items_container.children) == 0:
                pass
            else:
                self.ids.sidebar_items_container.clear_widgets()
            if len(self.ids.sidebar_footer_container.children) == 0:
                pass
            else:
                self.ids.sidebar_footer_container.clear_widgets()

            spawnItems([
                SidebarItem('s1_m1'),
                SidebarItem('s1_m2'),
                SidebarItem('s1_m3'),
            ])

        elif screen == 'for_screen2':
            printLog('sidebar', 'for screen2')
            self.ids.sidebar_items_container.clear_widgets()

            spawnItems([
                SidebarItem('s2_m1'),
                SidebarItem('s2_m2'),
                SidebarItem('s2_m3'),
            ])

            # spawn signout btn
            signout_button = SignoutButton()
            signout_button.bind(on_release = self.goToFirstScreen)
            self.ids.sidebar_footer_container.add_widget(signout_button)

    def showSidebar(self, *args):
        # animate
        anim = Animation(
            myX = 0,
            duration = .3,
            t = 'out_circ')
        anim.start(self.ids.sidebar)

        self._sidebar_shown_state = True
        printLog('sidebar', 'Showed')

        self.updateLayout(None, self.size)

    def closeSidebar(self, *args):
        anim = Animation(
            myX = -1,
            duration = .5,
            t = 'out_circ')
        anim.start(self.ids.sidebar)

        self._sidebar_shown_state = False
        printLog('sidebar', 'Closed')

        self.updateLayout(None, self.size)

    def loginAuth(self, *args):
        email = self._screen1.ids.email_login_field.text
        password = self._screen1.ids.password_login_field.text

        if email == 'admin' and password == 'admin':
            self.goToSecondScreen()
            printLog('log', 'berhasil login')
        else:
            pass

    def showLoginForm(self, *args):
        anim = Animation(
            my = 0,
            duration = .3,
            t = 'out_circ'
        ).start(self._screen1.ids.login_form)

        self.loginFormState('active')

    def removeLoginForm(self, *args):
        anim = Animation(
            my = -.5,
            duration = .2,
            t = 'out_circ'
        ).start(self._screen1.ids.login_form)

        self.loginFormState('inactive')

    def loginFormState(self, state):
        printLog('login form sate', state)
        barrier = ScreenBarrier()

        if state == 'active': # (jika login form telah muncul)
            # unbind func showLoginForm
            self._screen1.ids.get_started_btn.unbind(on_release = self.showLoginForm)
            # bind ke login func
            self._screen1.ids.get_started_btn.bind(on_release = self.goToSecondScreen)

            # ubah text
            self._screen1.ids.get_started_btn.text = 'Login'

            # pasang screen barrier
            self._screen1.ids.barrier_place.add_widget(barrier)

            # bind barrier untuk removeLoginForm
            barrier.bind(on_release = self.removeLoginForm)

            # bind manager.ids.menu_button + search_button > removeLoginForm
            self.ids.manager_menu_btn.bind(on_release = self.removeLoginForm)
            self.ids.manager_search_btn.bind(on_release = self.removeLoginForm)

        else: # (jika login form tidak muncul)
            # unbind func removeLoginForm
            self._screen1.ids.get_started_btn.unbind(on_release = self.removeLoginForm)

            # bind kembali func showLoginForm
            self._screen1.ids.get_started_btn.unbind(on_release = self.goToSecondScreen)
            self._screen1.ids.get_started_btn.bind(on_release = self.showLoginForm)

            # rubah text button menjadi awalnya
            self._screen1.ids.get_started_btn.text = 'Get Started'

            # menghapus barrier
            barrier.unbind(on_release = self.removeLoginForm)
            self._screen1.ids.barrier_place.clear_widgets()

            # unbind manager.ids.menu_button + search_button > removeLoginForm
            self.ids.manager_menu_btn.unbind(on_release = self.removeLoginForm)
            self.ids.manager_search_btn.unbind(on_release = self.removeLoginForm)

    def spawnPopup(self, color=(239/255, 105/255, 137/255, 1), title='title', message='message', *args):
        # declare popup
        popup = MyPopup()

        popup.canvas_color = color
        popup.title = title
        popup.message = message

        # spawn
        self.ids.popup_place.add_widget(popup)

        # animasikan setelah di spawn
        Animation(
            my_top = 1,
            duration = .2,
            t = 'out_circ'
        ).start(popup)

        # task untuk remove popup
        task = Clock.schedule_once(partial(
            self.removePopup,
            popup), 4)

        # func untuk membatalkan task
        def cancelTask(*args):
            task.cancel()

        printLog('popup log', 'popup placed')

    def removePopup(self, popup_instance, *args):
        def remove(*args):
            self.ids.popup_place.remove_widget(popup_instance)
            printLog('popup log', 'popup removed')

        # animasikan sebelum dihapus
        anim = Animation(
            my_top = 1.5,
            duration = .25,
            t = 'out_circ'
        )
        anim.start(popup_instance)
        anim.bind(on_complete = remove)

    def showLessPeopleSection(self, *args):
        self._screen2._home_page.ids.view_all_btn.text = 'view all'
        
        profile_section = self._screen2._home_page.ids.profile_card_container

        if len(profile_section.children) == len(self._people):
            profile_section.clear_widgets()
            printLog('log', 'clear widgets for every children in profile_section')
        else:
            pass

        # generate profile card pada profile section
        def generateCard(*args):
            for i in range(3):
                profile_section.add_widget(ProfileCard())
        Clock.schedule_once(generateCard)

        # memberikan identitas pada setiap profile card
        def setPersonInfo(*args):
            people_index = 2
            # karena container children bersifat reversed, maka index juga diambil dari belakang
            for child in profile_section.children:
                child.person_name = self._people[people_index].name
                child.person_role = self._people[people_index].role
                child.person_pict = self._people[people_index].photo_path

                child.ids.pick_person_btn.bind(
                    on_release = partial(
                        self.updateDonateCard,
                        child.person_name,
                        child.person_role,
                        child.person_pict
                    )
                )
                child.ids.pick_person_btn.bind(on_release = self._screen2.scrollToUp)

                people_index -= 1
        Clock.schedule_once(setPersonInfo)

        self._screen2._home_page.ids.view_all_btn.unbind(on_release = self.showLessPeopleSection)
        self._screen2._home_page.ids.view_all_btn.bind(on_release = self.showMorePeopleSection)

    def showMorePeopleSection(self, instance):
        self._screen2._home_page.ids.view_all_btn.text = 'view less'

        profile_section = self._screen2._home_page.ids.profile_card_container

        # menambah profile card
        profile_card_showed_total = len(profile_section.children)
        def generateCard(*args):
            for i in range(len(self._people)-profile_card_showed_total):
                profile_section.add_widget(ProfileCard())
        Clock.schedule_once(generateCard)

        # menampilkan sisa person
        def setPersonInfo(*args):
            people_index = len(self._people)-1
            for child in profile_section.children:
                if child.person_name == 'Unknown':
                    child.person_name = self._people[people_index].name
                    child.person_role = self._people[people_index].role
                    child.person_pict = self._people[people_index].photo_path

                    child.ids.pick_person_btn.bind(
                        on_release = partial(
                            self.updateDonateCard,
                            child.person_name,
                            child.person_role,
                            child.person_pict
                        )
                    )
                    child.ids.pick_person_btn.bind(on_release = self._screen2.scrollToUp)

                    people_index -= 1
        Clock.schedule_once(setPersonInfo)

        self._screen2._home_page.ids.view_all_btn.unbind(on_release = self.showMorePeopleSection)
        self._screen2._home_page.ids.view_all_btn.bind(on_release = self.showLessPeopleSection)
        # unbind view all button untuk auto scroll
        #self._screen2.ids.view_all_btn.unbind(on_release = self.scrollToDown)