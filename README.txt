===================
Memorize Flashcards
===================

Memorize flashcards provides a python module plus admin shell script
manage personal "courses" in the form of question/answer flashcards.
This can help memorize stuff of any kind- learning for exam in history
class or making your way to learning new language.
The admin tool provides the DB stuff, placing the "cards" files in
place, hashing the, etc, while the python module provides "policy"-
how often each card is shown.

A lesson
=========
A lesson is one "practice"- for example, going over 30 flashcards,
just before bed time.
The python module "policy.py" is responsible of choosing the cards for
a lesson.

A lesson should be comprised of, typically, the cards which the user
know least well. This is the job of the policy- to determine which
cards should play in the comming lesson.

It uses the cards *major* and *minor* numbers to do this.
A major number of card should tell how far the next lesson for this
card is. For example, major of value '1' means the next lesson should
contain this card, while major value of '8' means you will exersice
this card in 8 lessons.
The *minor* value of a card tells how well the user known the card.
A value of 1 means "not so well", while value of 256 means "this card
is well hard coded in the users brain".
Using these two values the policy should comprise the next lesson.

A lesson in act will be showing a card, showing the back side of it
(after pressing some key, or after waiting some amount of time), then
asking the user wheather he knew the card or not.
Then according to policy, update the major/minor values.

A classic policy
================
Suppose we have a card with major/minor values of 1/2. So in the
comming lesson the card will be shown.
If the user knew the card, a classic policy would push it back to a
distant lesson. How distant? minor+major, meaning 3. This means that
knowing a card doubles the time untill seeing it again. The minor
number is doubled as well, so the new major/manor values are 3/4.
If the user didn't know the card, the policy would want to show
it next lesson again, and the freequency of showing it should be high,
so in this case the major/minor number would be 2/1.

Policies can be added by inheriting from "Policy" and implmementing
fetch_card() and update_card().	

For example, the classic policy update card function looks somthing
like::

	def update_card(self, card, value):
		if (card in self.cards) or (card in self.used_pile):
			raise Exception("Illegal state- card must be out of pile and used pile when updated")
		#print "D: card lesson before: {}".format(card.lesson)
		if (value == True):
			card.lesson += card.period
			card.period *= 2
		else: # value == False
			card.lesson += 1
			card.period = 1
		self.used_pile.append(card)
		#print "D: card lesson after: {}".format(card.lesson)

A client
=========

Client is a script that uses the policy module and admin tool to
actually present the cards and using the policy and admin tool to
update the DB.

A very basic one is currently implemented, which is the
`memorize-flashcards-konsole-client`.
