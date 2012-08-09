TeamRouter = Backbone.Router.extend({
    routes: {
        '': 'sort',
        'sort/:sortId': 'sort',
        'sort/:sortId/user/:username': 'sort',
        'user/:username': 'username'
    },

    defaultSortId: 'random',

    initialize: function(options) {
        this.sortState = options.sortState
        this.popup = options.popup
        this.grids = options.grids

        options.popup.on('show hide', this.updateState, this)
    },

    updateState: function() {
        var url = [],
            sortId = this.sortState.get('sort'),
            username = this.popup.model && this.popup.model.id

        if (sortId && !(username && sortId == this.defaultSortId)) {
            url.push('sort/' + sortId)
        }

        if (username) {
            url.push('user/' + username)
        }

        this.navigate(url.join('/'), {replace: true})
    },

    sort: function(sortId, username) {
        if (!sortId && !this.sortState.has('sort')) {
            sortId = this.defaultSortId
        }

        if (sortId) {
            this.sortState.set('sort', sortId)
        }

        if (username) {
            this.username(username)
        }
    },

    username: function(username) {
        this.sort()

        // Defer so that target view has final position if sort changed.
        _.defer(_.bind(function() {
            _.find(this.grids, function(grid) {
                grid.showPopup(username, true)
            })
        }, this))
    }
})

DropdownView = Backbone.View.extend({
    events: {
        'click .choice': 'select'
    },

    initialize: function(options) {
        this.attribute = options.attribute
        this.model.on('change:' + this.attribute, this.render, this)
    },

    render: function() {
        var choice = this.model.get(this.attribute),
            $choice = this.$('.drop-choices .choice-' + choice)

        this.$('.drop-choices .selected').removeClass('selected')
        $choice
            .addClass('selected')
            .removeClass('hidden-sort')
        this.$('.dropdown .selected').text($choice.text())
        return this
    },

    select: function(e) {
        var choice = $(e.target).attr('class').match(/choice-(.*)/)[1]
        this.model.set(this.attribute, choice)
        this.trigger('select', choice)
    }
})

TeamMember = Backbone.Model.extend({
    idAttribute: 'username',

    initialize: function() {
        this.set('random', Math.random())
    }
})

SortableCollection = Backbone.Collection.extend({
    model: TeamMember,

    initialize: function(models, options) {
        this.sorts = options.sorts
        this.state = options.state || new Backbone.Model({
            sort: null
        })
        this.state.on('change:sort', this.sort, this)
    },

    comparator: function(model) {
        var sort = this.sorts.get(this.state.get('sort'))
        if (!sort) {
            return
        }

        var sortVal = model.get(sort.id)
        if (_.isNumber(sortVal)) {
            sortVal = sortVal * sort.get('dir')
        } else if (_.isString(sortVal)) {
            sortVal = sortVal.toLowerCase()
        }
        return sortVal || model.get('random')
    }
})

PersonDetailsPopup = Backbone.View.extend({
    id: 'person-overlay',
    events: {
        'click .close': 'hide'
    },

    template: _.template(
         '<button class="close">x</button><div class="top">'
            +'<strong class="name"><%= d.name %></strong>'
            +'<em class="role" title="<%= d.role_details %>"><%= d.role %></em>'
        +'</div>'
        +'<div class="description">'
            +'<p><%= d.description %></p>'
            +'<div class="favorite-subreddits"><span>favorite subreddits:</span><ul></ul></div>'
        +'</div>'
        +'<div class="etc"><a href="http://www.reddit.com/user/<%= d.username %>" target="_blank">reddit.com/user/<%= d.username %></a></div>'
    ),

    initialize: function() {
        $('body').click(_.bind(function(ev) {
            if (!this.targetView) {
                return
            }

            if (!$(ev.target).closest($([this.el, this.targetView.el])).length) {
                this.hide()
            }
        }, this))
        $(window).resize(_.bind(this.position, this))
    },

    render: function() {
        this.$el.empty().append(this.template(this.model.toJSON()))
        var favorite_srs = this.$('.favorite-subreddits ul')
        _.each(this.model.get('favorite_subreddits'), function(sr) {
            $('<li>').append(
                $('<a>')
                    .attr('href', sr)
                    .text(sr)
            ).appendTo(favorite_srs)
        })
    },

    position: function() {
        if (!this.targetView) {
            return
        }

        var avatar = this.targetView.$('.avatar'),
            personPos = avatar.offset(),
            parent = this.$el.parent(),
            leftSide = personPos.left < parent.offset().left + parent.width() / 2

        this.$el
            .css({
                top: personPos.top,
                left: personPos.left + (leftSide ? avatar.outerWidth(true) : -this.$el.width())
            })
            .removeClass('left right')
            .addClass(leftSide ? 'left' : 'right')
    },

    show: function(view) {
        this.hide(true)
        this.targetView = view
        this.model = view.model

        this.render()
        this.position()
        this.$el.show()

        this.targetView.$el.addClass('focused')
        this.trigger('show', this.model)
    },

    hide: function(isChange) {
        var oldModel = this.model
        this.model = null
        if (this.targetView) {
            this.targetView.$el.removeClass('focused')
            this.targetView = null
            if (!isChange) {
                this.trigger('hide', oldModel)
            }
        }
        this.$el.hide()
    },

    toggle: function(view) {
        if (view == this.targetView) {
            this.hide()
        } else {
            this.show(view)
        }
    }
})

PersonView = Backbone.View.extend({
    events: {
        'click': 'showInfo'
    },

    showInfo: function() {
        this.options.popup.toggle(this)
    }
})

PeopleGridView = GridView.extend({
    initialize: function() {
        GridView.prototype.initialize.apply(this)
        this.collection.on('reset', this.options.popup.hide, this.options.popup)
        this.options.popup
            .on('show', this.focus, this)
            .on('hide', this.unfocus, this)
    },

    createItemView: function(model) {
        return new PersonView({
            el: this.$('.'+model.id),
            model: model,
            popup: this.options.popup
        })
    },

    showPopup: function(username, scroll) {
        var view = this.itemViews[username]
        if (!view) {
            return false
        }

        this.options.popup.show(view)

        if (scroll) {
            var viewBottom = view.$el.offset().top + view.$el.height()
            $(window).scrollTop(Math.max(0, viewBottom - $(window).height() / 2))
        }

        return view
    },

    focus: function(model) {
        this.$el.addClass('focusing')
        $('.content').addClass('focusing-' + model.id)
    },

    unfocus: function(model) {
        this.$el.removeClass('focusing')
        $('.content').removeClass('focusing-' + model.id)
    }
})

teamSorts = new Backbone.Collection
team = new SortableCollection(null, {sorts: teamSorts})
alumni = new SortableCollection(null, {sorts: teamSorts, state: team.state})

r.about.pages['about-team'] = function() {
    var sortDropdown = new DropdownView({
        el: $('#about-team .sort-menu'),
        model: team.state,
        attribute: 'sort'
    })

    new scrollFixed($('#about-team .sort-menu'))

    var personPopup = new PersonDetailsPopup()
    $('#about-team').append(personPopup.el)

    var teamGrid = new PeopleGridView({
        el: $('#team-grid'),
        collection: team,
        popup: personPopup
    })

    var alumniGrid = new PeopleGridView({
        el: $('#alumni-grid'),
        collection: alumni,
        popup: personPopup
    })

    var sortRouter = new TeamRouter({
        sortState: team.state,
        popup: personPopup,
        grids: [teamGrid, alumniGrid]
    })

    Backbone.history.start()
}
