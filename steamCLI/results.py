class Results:
    def __init__(self, result=None, center=79):
        if result is None:
            self.result = []
        else:
            self.result = result
        self.center = center

    def construct_steam_info(self, app):
        rel_date = app.release_date if app.release_date else 'no release date'
        initial = round(app.initial / 100, 2) if app.initial else 'N/A'
        current = round(app.current / 100, 2) if app.current else 'N/A'
        currency = f' {app.currency}' if app.currency else ""

        self.result.append(f'*** {app.title} ({rel_date}) ***')
        self.result.append(f'{current}{currency} ({app.discount}% '
                           f'from {initial}{currency})')
        self.result.append(f'Metacritic score: {app.meta}')

        return '\n'.join(line.center(self.center) for line in self.result)
