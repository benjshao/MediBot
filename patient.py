class Patient:
  def __init__(self, member, medication, amount, reminder):
    self.member = member
    self.medication = medication
    self.amount = amount
    self.reminder = reminder

    def __call__(self):
        return self
