AboutSlideshowView = SlideshowView.extend({
    interval: 10*1000,
    render: function() {
        SlideshowView.prototype.render.apply(this)
        var image = this.collection.at(this.index)
        this.$('.title')
            .attr('href', image.get('url'))
            .text(image.get('title'))
        this.$('.author')
            .attr('href', image.get('author_url'))
            .text(image.get('author'))
        this.$('.user')
            .attr('href', image.get('via_url'))
            .text(image.get('via'))
        this.$('.comments')
            .attr('class', image.get('comment_class'))
            .attr('href', image.get('permalink'))
            .addClass('comments')
            .text(image.get('comment_label'))
        return this
    }
})

AboutTimelineView = TimelineView.extend({
    rowHeight: 30,

    filter: function(model) {
        return ~model.get('class').indexOf('important')
    },

    filterTop: function(model) {
        return ~model.get('class').indexOf('org')
    }
})

slideshowImages = new Backbone.Collection

r.about.pages['about-main'] = function() {
    var slideshow = new AboutSlideshowView({
        el: $('#slideshow'),
        collection: slideshowImages
    }).play()

    var timeline = new AboutTimelineView({
        el: $('#history .events')
    }).render()
}
