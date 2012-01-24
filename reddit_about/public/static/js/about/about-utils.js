function scrollFixed(el) {
    this.$el = $(el)
    this.$clone = null
    this.origTop = this.$el.position().top
    this.onScroll()
    $(window).scroll(_.bind(this.onScroll, this))
}
scrollFixed.prototype = {
    onScroll: function() {
        if ($(window).scrollTop() > this.origTop) {
            if (!this.$clone) {
                this.$clone = this.$el.clone()
                this.$clone
                    .appendTo(this.$el.parent())
                    .css({
                        position: 'fixed',
                        top: 0
                    })
            }
        } else {
            if (this.$clone) {
                this.$clone.remove()
                this.$clone = null
            }
        }
    }
}
